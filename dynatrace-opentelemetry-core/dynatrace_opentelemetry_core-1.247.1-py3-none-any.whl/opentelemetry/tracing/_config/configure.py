from typing import Optional

from dynatrace.opentelemetry.tracing._config import reader
from dynatrace.opentelemetry.tracing._export.exporter import DtSpanExporter
from dynatrace.opentelemetry.tracing._export.processor import DtSpanProcessor
from dynatrace.opentelemetry.tracing._otel.api import _trace as api_trace
from dynatrace.opentelemetry.tracing._otel.api import set_global_textmap
from dynatrace.opentelemetry.tracing._otel.sdk import Resource, TracerProvider
from dynatrace.opentelemetry.tracing._propagator.textmap import (
    DtTextMapPropagator,
)
from dynatrace.opentelemetry.tracing._sampler import DT_SAMPLER


def configure_dynatrace(resource: Optional[Resource] = None) -> TracerProvider:
    config = reader.get_configuration()

    tpargs = {"sampler": DT_SAMPLER}
    if resource is not None:
        tpargs["resource"] = resource

    tracer_provider = TracerProvider(**tpargs)

    set_global_textmap(DtTextMapPropagator(config=config))

    exporter = DtSpanExporter(config=config)
    processor = DtSpanProcessor(exporter=exporter, config=config)
    tracer_provider.add_span_processor(processor)

    api_trace.set_tracer_provider(tracer_provider)

    return tracer_provider
