from typing import Optional

from dynatrace.opentelemetry.tracing._otel.api import (
    INVALID_SPAN_CONTEXT,
    SpanContext,
)
from dynatrace.opentelemetry.tracing._otel.sdk import ReadableSpan
from dynatrace.opentelemetry.tracing._propagator.tags import Fw4Tag


def get_parent_span_context(span: ReadableSpan) -> SpanContext:
    if not isinstance(span, ReadableSpan):
        return INVALID_SPAN_CONTEXT
    parent = span.parent
    return parent if parent is not None else INVALID_SPAN_CONTEXT


def get_tenant_parent_span_id(
    parent_context: SpanContext, fw4_tag: Fw4Tag
) -> Optional[int]:
    if not parent_context or not parent_context.is_valid:
        return None
    if not parent_context.is_remote:
        # for local spans it is always the span ID of the parent
        return parent_context.span_id
    if fw4_tag and fw4_tag.has_span_id:
        # for a remote span the FW4 tag holds the last known parent span
        # of the tenant
        return fw4_tag.span_id
    return None
