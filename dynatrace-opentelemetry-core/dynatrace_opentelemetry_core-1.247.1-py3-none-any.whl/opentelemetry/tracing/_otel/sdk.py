try:
    import dynatraceotel  # noqa: F401 pylint:disable=unused-import
except ImportError:
    from opentelemetry.sdk import resources as _resources
    from opentelemetry.sdk import trace as _trace
    from opentelemetry.sdk.trace import export as _export
    from opentelemetry.sdk.trace import sampling as _sampling
else:
    from dynatraceotel.sdk import resources as _resources
    from dynatraceotel.sdk import trace as _trace
    from dynatraceotel.sdk.trace import export as _export
    from dynatraceotel.sdk.trace import sampling as _sampling

# trace
Event = _trace.Event
ReadableSpan = _trace.ReadableSpan
Span = _trace.Span
SpanProcessor = _trace.SpanProcessor
TracerProvider = _trace.TracerProvider


# trace.resources
Resource = _resources.Resource

# trace.export
SpanExporter = _export.SpanExporter
SpanExportResult = _export.SpanExportResult

# trace.sampling
Decision = _sampling.Decision
ParentBased = _sampling.ParentBased
Sampler = _sampling.Sampler
SamplingResult = _sampling.SamplingResult
