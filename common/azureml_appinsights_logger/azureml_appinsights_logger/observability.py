from azureml.core import Run

from .env_variables import Env
from .appinsights_logger import AppInsightsLogger
from .azureml_logger import AzureMlLogger
from .console_logger import ConsoleLogger
from .logger_interface import (
    ObservabilityAbstract,
    LoggerInterface,
    Severity,
)


class Loggers(ObservabilityAbstract):
    def __init__(self) -> None:
        print('Initializing the Loggers')
        self.loggers: LoggerInterface = []
        self.register_loggers()

    def add(self, logger) -> None:
        self.loggers.append(logger)

    def get_loggers_string(self) -> None:
        return ", ".join([type(x).__name__ for x in self.loggers])

    def register_loggers(self):
        """
        This method is responsible to create loggers/tracers
        and add them to the list of loggers
        Notes:
        - If the context of the Run object is offline,
        we do not create AzureMlLogger instance
        - If APPLICATIONINSIGHTS_CONNECTION_STRING is notset
        to ENV variable, we do not create AppInsightsLogger
        instance
        """
        run = Run.get_context()
        e = Env()
        if not run.id.startswith(self.OFFLINE_RUN):
            print("Registered AML Logger")
            self.loggers.append(AzureMlLogger(run))
        if e.app_insights_connection_string:
            if "InstrumentationKey" in e.app_insights_connection_string:
                print("Registered AppInsights Logger")
                self.loggers.append(AppInsightsLogger(run))
        if e.log_to_console:
            print("Registered Console Logger")
            self.loggers.append(ConsoleLogger(run))


class Observability(LoggerInterface):
    _instance = None

    # Straightforward Singleton Pattern from
    # https://python-patterns.guide/gang-of-four/singleton/
    def __new__(cls):
        if cls._instance is None:
            print('Creating the Observability Singleton')
            cls._instance = super(Observability, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self) -> None:
        if(not self.__initialized):
            print('Initializing the Observability Singleton')
            self.__initialized = True
            self._loggers = Loggers()

    def log_metric(
            self, name="", value="", description="", log_parent=False,
    ):
        """
        this method sends the metrics to all registered loggers
        :param name: metric name
        :param value: metric value
        :param description: description of the metric
        :param log_parent: (only for AML), send the metric to the run.parent
        :return:
        """
        for logger in self._loggers.loggers:
            logger.log_metric(name, value, description, log_parent)

    def log(self, description="", severity=Severity.INFO):
        """
        this method sends the logs to all registered loggers
        :param description: Actual log description to be sent
        :param severity: log Severity
        :return:
        """
        for logger in self._loggers.loggers:
            logger.log(description, severity)

    def exception(self, exception: Exception):
        """
        this method sends the exception to all registered loggers
        :param exception: Actual exception to be sent
        :return:
        """
        for logger in self._loggers.loggers:
            logger.exception(exception)

    def get_logger(self, logger_class):
        """
        This method iterate over the loggers and it
        returns the logger with the same type as the provided one.
        this is a reference that can be used in case
        any of the built in functions of the loggers is required
        :param logger_class:
        :return: a logger class
        """
        for logger in self._loggers.loggers:
            if type(logger) is type(logger_class):
                return logger

    def span(self, name='span'):
        """Create a new span with the trace using the context information
           for all registered loggers.
        :type name: str
        :param name: The name of the span.
        :rtype: :class:`~opencensus.trace.span.Span`
        :returns: The Span object.
        """
        for logger in self._loggers.loggers:
            logger.span(name)
        return self.current_span()

    def start_span(self, name='span'):
        """Start a span for all registered loggers.
        :type name: str
        :param name: The name of the span.
        :rtype: :class:`~opencensus.trace.span.Span`
        :returns: The Span object.
        """
        for logger in self._loggers.loggers:
            logger.start_span(name)
        return self.current_span()

    def end_span(self):
        """End a span for all registered loggers.
        Remove the span from the span stack, and update the
        span_id in TraceContext as the current span_id which is the peek
        element in the span stack.
        """
        for logger in self._loggers.loggers:
            logger.end_span()

    def current_span(self):
        """Return the current span from first logger"""
        if len(self._loggers.loggers) > 0:
            return self._loggers.loggers[0].current_span()

    def add_attribute_to_current_span(self, attribute_key, attribute_value):
        """Add attribute to current span for all registered loggers.
        """
        for logger in self._loggers.loggers:
            logger.add_attribute_to_current_span(attribute_key,
                                                 attribute_value)

    def list_collected_spans(self):
        """List collected spans from first logger."""
        if len(self._loggers.loggers) > 0:
            return self._loggers.loggers[0].list_collected_spans()


observability = Observability()
