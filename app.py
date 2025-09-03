import time, random
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 🔥 Ajout d’un resource avec service.name
resource = Resource.create({"service.name": "demo-python"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("demo-python")

exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

print("Envoi de traces… (Ctrl+C pour arrêter)")
while True:
    with tracer.start_as_current_span("operation-principale"):
        with tracer.start_as_current_span("operation-enfant"):
            time.sleep(random.uniform(0.1, 0.4))
    time.sleep(2)
