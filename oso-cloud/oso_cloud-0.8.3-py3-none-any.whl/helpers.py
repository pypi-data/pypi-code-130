from typing import cast, Dict, Optional, List

from . import api


def to_typed_id(instance):
    if instance is None:
        raise TypeError(
            f'Oso: No type and id present on instance passed to Oso: {instance}\n\nAll objects passed to Oso must either be strings or have a type and id property, like:\n\t{{ type: "User", id: "alice" }}'
        )
    if isinstance(instance, str):
        if instance == "":
            raise TypeError("Instance can not be an empty string")
        return api.TypedId("String", instance)
    if (
        "type" not in instance
        or instance["type"] is None
        or "id" not in instance
        or instance["id"] is None
    ):
        raise TypeError(
            f'Oso: No type and id present on instance passed to Oso: {instance}\n\nAll objects passed to Oso must either be strings or have a type and id property, like:\n\t{{ type: "User", id: "alice" }}'
        )
    return api.TypedId(instance["type"], instance["id"])


def from_typed_id(typedId):
    if isinstance(typedId, dict):
        return typedId
    if typedId.type == "String":
        return typedId.id
    return {"id": typedId.id, "type": typedId.type}


def to_variable(instance):
    if instance is None:
        return api.Variable("FreeVariable", None)
    if isinstance(instance, str):
        if instance == "":
            raise TypeError(
                "Oso: Instance cannot be an empty string. For wildcards, use the empty dict ({}) or None."
            )
        return api.Variable("TypedId", api.TypedId("String", instance))
    if "id" not in instance or instance["id"] is None:
        if "type" not in instance or instance["type"] is None:
            return api.Variable("FreeVariable", None)
        return api.Variable("TypedVariable", api.TypedVar(instance["type"]))

    if "type" not in instance or instance["type"] is None:
        raise TypeError(f"Oso: Instances with an ID must also have a type: {instance}")
    return api.Variable("TypedId", api.TypedId(instance["type"], instance["id"]))


def from_variable(variable):
    if variable.kind == "FreeVariable":
        return None
    if variable.kind == "TypedVariable":
        assert isinstance(variable.value, api.TypedVar)
        return {"type": variable.value.type}
    if variable.kind == "TypedId":
        assert isinstance(variable.value, api.TypedId)
        return {"type": variable.value.type, "id": variable.value.id}
    raise TypeError(f"Invalid variable: {variable}")


def param_to_fact(predicate, *args):
    return api.Fact(predicate, [to_typed_id(a) for a in args])


def map_params_to_facts(params):
    if not params:
        return []
    return [param_to_fact(*param) for param in params]


def fact_to_param(fact):
    if isinstance(fact, api.Fact):
        return [fact.predicate, *[from_typed_id(a) for a in fact.args]]
    if isinstance(fact, api.VariableFact):
        return [fact.predicate, *[from_variable(a) for a in fact.args]]
    print(fact)
    assert False


def map_facts_to_params(facts):
    if not facts:
        return []
    return [fact_to_param(fact) for fact in facts]
