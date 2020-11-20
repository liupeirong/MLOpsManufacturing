import inspect
from opencensus.trace.tracer import Tracer


class Severity:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LoggerInterface(Tracer):

    def log_metric(self, name, value, description, log_parent):
        pass

    def log(self, name, value, description, severity, log_parent):
        pass

    def finish(self):
        """End the spans and send to reporters."""
        pass

    def span(self, name='span'):
        """Create a new span with the trace using the context information.
        :type name: str
        :param name: The name of the span.
        :rtype: :class:`~opencensus.trace.span.Span`
        :returns: The Span object.
        """
        pass

    def start_span(self, name='span'):
        """Start a span.
        :type name: str
        :param name: The name of the span.
        :rtype: :class:`~opencensus.trace.span.Span`
        :returns: The Span object.
        """
        pass

    def end_span(self):
        """End a span. Remove the span from the span stack, and update the
        span_id in TraceContext as the current span_id which is the peek
        element in the span stack.
        """
        pass

    def current_span(self):
        """Return the current span."""
        pass

    def add_attribute_to_current_span(self, attribute_key, attribute_value):
        pass

    def list_collected_spans(self):
        """List collected spans."""
        pass


class ObservabilityAbstract:
    OFFLINE_RUN = "OfflineRun"
    CORRELATION_ID = "correlation_id"
    severity = Severity()
    severity_map = {10: "DEBUG", 20: "INFO",
                    30: "WARNING", 40: "ERROR", 50: "CRITICAL"}

    @staticmethod
    def get_callee(stack_level):
        """
        This method get the callee location in [file_name:line_number] format
        :param stack_level:
        :return: string of [file_name:line_number]
        """
        try:
            stack = inspect.stack()
            file_name = stack[stack_level + 1].filename.split("/")[-1]
            line_number = stack[stack_level + 1].lineno
            return "{}:{}".format(file_name, line_number)
        except IndexError:
            print("Index error, failed to log to AzureML")
            return ""
