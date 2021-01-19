import os
import re
import logging
from typing import Union
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer, SpanContext
from opencensus.trace.propagation.trace_context_http_header_format import TraceContextPropagator
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import view as view_module
from opencensus.trace import config_integration

class OpenCensusLogger():
    """
    This is a helper class which encapsulates the required boilerplate
    code for OpenCensus to connect to Application Insights and properly
    correlate telemetry for incoming requests.

    Methods
    -------
    log_metric(measure_name=None, value=None, description=None)
        Log a numeric metric such as scoring_time, with an optional description

    log_message(log_level=None, log_msg=None)
        Log a message to application insights with the specified level.
        Levels include logging.INFO, logging.DEBUG, logging.WARNING, logging.ERROR, logging.CRITICAL

    get_tracer(request_headers=None)
        Create an OpenCensus Tracer object with a SpanContext set to match
        the 'traceparent' details in request_headers.
    """

    def __init__(self, cloud_role_name='ML Scoring Container'):
        self.__verify_instrumentation_key()
        self.__initialize_metric_helpers()
        self.__initialize_log_helpers()

        # initialize empty metric dictionary
        # these are key-value pairs of name -> measure
        # where measure is an OpenCensus class
        self._measures = {}
        self._cloud_role_name = cloud_role_name

    def __add_cloud_role(self, envelope):
        envelope.tags['ai.cloud.role'] = self._cloud_role_name

    def __initialize_metric_helpers(self):
        """
        Initialize OpenCensus classes needed for metrics
        """
        exporter = metrics_exporter.new_metrics_exporter(export_interval=30)
        exporter.add_telemetry_processor(self.__add_cloud_role)
        stats = stats_module.stats
        self._view_manager = stats.view_manager
        self._stats_recorder = stats.stats_recorder
        self._view_manager.register_exporter(exporter)
        self.mmap = self._stats_recorder.new_measurement_map()

    def __initialize_log_helpers(self):
        """
        Initialize OpenCensus handler and registers to python logger
        """
        # Attach the traceId and spanId to logs generated during a run using trace_integrations
        config_integration.trace_integrations(['logging'])
        logging.basicConfig(format='%(asctime)s traceId=%(traceId)s spanId=%(spanId)s %(message)s')

        self._opencensus_logger = logging.getLogger(__name__)

        # set minimum level for logs to be displayed at
        self._opencensus_logger.setLevel(logging.INFO)
        handler = AzureLogHandler()
        handler.add_telemetry_processor(self.__add_cloud_role)
        self._opencensus_logger.addHandler(handler)
        self._log_exporter = AzureExporter(
            connection_string=os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING'),
            export_interval=30)
        self._log_exporter.add_telemetry_processor(self.__add_cloud_role)


    def __register_measure(self, measure_name: str, description: str = None, measure_type: str = 'float'):
        """
        Creates measure and adds it to _measures dictionary
        Registers View, which includes a specific aggregation and a set of tag keys
        this allows it to be viewable & queryable in App Insights.
        """
        # Int is for counting
        if measure_type == 'int':
            measure = measure_module.MeasureInt(name=measure_name, description=description)
            aggregation = aggregation_module.CountAggregation()
        # Float is for logging the value
        elif measure_type == 'float':
            measure = measure_module.MeasureFloat(name=measure_name, description=description)
            aggregation = aggregation_module.LastValueAggregation()
        else:
            raise Exception("Invalid metric type")

        view = view_module.View(name=measure_name,
                                description=description,
                                columns=[],
                                measure=measure,
                                aggregation=aggregation)

        self._view_manager.register_view(view)
        self._measures[measure_name] = measure

    def log_metric(self, measure_name: str, value: Union[int, float], description: str = None):
        """
        Logs metric to App Insights:
        If passed an int, it will increment that value as a counter. If passed a float,
        it will log the last value.
        """
        # If we haven't seen this measure before, register it
        if measure_name not in self._measures:
            self.__register_measure(measure_name, description, measure_type=('int' if isinstance(value, int) else 'float'))

        # get OpenCensus measure to log metric
        measure = self._measures[measure_name]

        tmap = tag_map_module.TagMap()
        if isinstance(value, int):
            self.mmap.measure_int_put(measure, value)
        else:
            self.mmap.measure_float_put(measure, value)
        self.mmap.record(tmap)

    def log_message(self, log_level: int, log_msg: str):
        """
        Logs message with given level to Application Insights
        """
        self._opencensus_logger.log(level=log_level, msg=log_msg)

    def __check_view_exists(self, view_name):
        view = self._view_manager.get_view(view_name)
        if view is not None:
            return view.view.name == view_name
        return False

    @staticmethod
    def __verify_instrumentation_key():
        """
        Verifies instrumentation key env variable
        """
        if not os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING'):
            raise Exception("Environment variable APPLICATIONINSIGHTS_CONNECTION_STRING is not set")

    def get_tracer(self, request_headers):
        """
        This method builds an OpenCensus Tracer object to allow for
        distributed tracing within App Insights/Azure Monitor
        :param request_headers: A dictionary of headers passed to the
        container by the service calling it. The primary value of
        importance is Traceparent - the Trace Context HTTP header which
        contains the operation id and parent id of the service calling
        this.
        Expected format of Traceparent is 00-00000000000000000000000000000000-0000000000000000-00
        Values all may be 0-9, a-f.
        :returns: Tracer object with context set to correlate with the
        incoming request. If the header is malformed, it sets the span_id to None, and
        generates a unique trace_id, rather than failing.
        """
        if request_headers.get("Traceparent") is not None:
            traceparent = request_headers.get("Traceparent")
            trace_info = traceparent.split("-")
            # Validate that the Traceparent header contained all 4 expected components
            # See https://www.w3.org/TR/trace-context/#trace-context-http-headers-format for info
            if len(trace_info) == 4:
                trace_id = trace_info[1]
                span_id = trace_info[2]
                # Validate that the trace_id and span_id are correctly formatted
                if not re.match('[0-9a-f]{32}', trace_id) or not re.match('[0-9a-f]{16}', span_id):
                    self._opencensus_logger.log(
                        logging.WARNING,
                        'TraceParent header is malformed. TraceID and/or SpanID will not correlate to originating call'
                        )
                # Create a SpanContext which links the traces back to the operation_id and parent of the
                # incoming request
                span_context = SpanContext(trace_id=trace_id, span_id=span_id)
            else:
                self._opencensus_logger.log(
                        logging.WARNING,
                        'TraceParent header is malformed. TraceID and/or SpanID will not correlate to originating call'
                        )
                span_context = SpanContext()

            tracer = Tracer(
                sampler=ProbabilitySampler(rate=1.0),
                exporter=self._log_exporter,
                span_context=span_context,
                propagator=TraceContextPropagator()
                )
        else:
            tracer = Tracer(
                sampler=ProbabilitySampler(rate=1.0),
                exporter=self._log_exporter,
                propagator=TraceContextPropagator()
            )
        return tracer
