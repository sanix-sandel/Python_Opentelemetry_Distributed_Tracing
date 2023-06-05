from flask import Flask, request
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry import context
from opentelemetry.propagate import extract
from common import configure_tracer

tracer = configure_tracer("0.1.2", "grocery-store")
app = Flask(__name__)


# We need to get the context before the decorator instantiates the span
@app.before_request
def before_request_func():
    token = context.attach(extract(request.headers))
    request.environ["context_token"] = token

@app.teardown_request
def teardown_request_func(err):
    token = request.environ.get("context_token", None)
    if token:
        context.detach(token)


@app.route("/")
@tracer.start_as_current_span("welcome", kind=SpanKind.SERVER)
def welcome():
    span = trace.get_current_span()
    span.set_attributes(
        {
            SpanAttributes.HTTP_FLAVOR: request.environ.get("SERVER_PROTOCOL"),
            SpanAttributes.HTTP_METHOD: request.method,
            SpanAttributes.HTTP_USER_AGENT: str(request.user_agent),
            SpanAttributes.HTTP_HOST: request.host,
            SpanAttributes.HTTP_SCHEME: request.scheme,
            SpanAttributes.HTTP_TARGET: request.path,
            SpanAttributes.HTTP_CLIENT_IP: request.remote_addr
        }
    )
    return "Welcome to the grocery store !"


if __name__ == "__main__":
    app.run(debug=True)
