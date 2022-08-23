from logging import Logger, getLogger

_NAMESPACE = "dynatrace.tracing"

_LOGGER_ALIAS_MAPPING = {}


def add_alias(alias: str, logger_name: str):
    _LOGGER_ALIAS_MAPPING[alias.lower()] = logger_name


def add_alias_and_get_logger(alias: str, logger_name: str) -> Logger:
    add_alias(alias, logger_name)
    return getLogger(logger_name)


def get_logger_name_from(alias_or_name: str) -> str:
    if not alias_or_name:
        return alias_or_name
    return _LOGGER_ALIAS_MAPPING.get(alias_or_name.lower(), alias_or_name)


################################################################################
# core package loggers
################################################################################

_KEY_CORE = "Core"
_KEY_EXPORTER = "Exporter"
_KEY_SERIALIZATION = "Serialization"
_KEY_PROCESSOR = "SpanProcessor"
_KEY_PROPAGATOR = "Propagator"

_LOGGER_NAME_CORE = f"{_NAMESPACE}.core"
_LOGGER_NAME_EXPORTER = f"{_NAMESPACE}.export.exporter"
_LOGGER_NAME_SERIALIZATION = f"{_NAMESPACE}.export.serialization"
_LOGGER_NAME_PROCESSOR = f"{_NAMESPACE}.export.processor"
_LOGGER_NAME_PROPAGATOR = f"{_NAMESPACE}.propagator"


core_logger = add_alias_and_get_logger(_KEY_CORE, _LOGGER_NAME_CORE)
exporter_logger = add_alias_and_get_logger(
    _KEY_EXPORTER, _LOGGER_NAME_EXPORTER
)
serialization_logger = add_alias_and_get_logger(
    _KEY_SERIALIZATION, _LOGGER_NAME_SERIALIZATION
)
processor_logger = add_alias_and_get_logger(
    _KEY_PROCESSOR, _LOGGER_NAME_PROCESSOR
)
propagator_logger = add_alias_and_get_logger(
    _KEY_PROPAGATOR, _LOGGER_NAME_PROPAGATOR
)

################################################################################
# non core package loggers
################################################################################
# TODO: add these via entry points
_KEY_TRACER = "Tracer"
_KEY_LAMBDA_SENSOR = "LambdaSensor"
_KEY_LAMBDA_SDK_SENSOR = "AwsLambdaSdkSensor"

_LOGGER_NAME_TRACER = f"{_NAMESPACE}.tracer"
_LOGGER_NAME_LAMBDA_SENSOR = f"{_NAMESPACE}.sensors.awslambda.incoming"
_LOGGER_NAME_LAMBDA_SDK_SENSOR = f"{_NAMESPACE}.sensors.awslambda.outgoing"

tracer_logger = add_alias_and_get_logger(_KEY_TRACER, _LOGGER_NAME_TRACER)
lambda_logger = add_alias_and_get_logger(
    _KEY_LAMBDA_SENSOR, _LOGGER_NAME_LAMBDA_SENSOR
)
lambda_sdk_logger = add_alias_and_get_logger(
    _KEY_LAMBDA_SDK_SENSOR, _LOGGER_NAME_LAMBDA_SDK_SENSOR
)

_KEY_AZURE = "Azure"
_LOGGER_NAME_AZURE = f"{_NAMESPACE}.azure"
azure_logger = add_alias_and_get_logger(_KEY_AZURE, _LOGGER_NAME_AZURE)

_KEY_GCF = "GoogleCloudFunctions"
_LOGGER_NAME_GCF = f"{_NAMESPACE}.gcf"
gcf_logger = add_alias_and_get_logger(_KEY_GCF, _LOGGER_NAME_GCF)

################################################################################
# backwards compatibility to old logger names
################################################################################
add_alias("dynatrace.agent.exporter", _LOGGER_NAME_EXPORTER)
add_alias("dynatrace.agent.exporter-serialize", _LOGGER_NAME_SERIALIZATION)
add_alias("dynatrace.agent.propagator", _LOGGER_NAME_PROPAGATOR)
add_alias("dynatrace.sensors.awslambda.incoming", _LOGGER_NAME_LAMBDA_SENSOR)
add_alias(
    "dynatrace.sensors.awslambda.outgoing", _LOGGER_NAME_LAMBDA_SDK_SENSOR
)
