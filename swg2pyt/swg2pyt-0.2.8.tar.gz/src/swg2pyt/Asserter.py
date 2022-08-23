from json import dumps as jsd
from json import loads as jsl

import jmespath

from .Pretreator import Pretreator, prt

INVALIDPATH = "Invalid path: {}"
UNSUPPORTED = "Unsupported assertion type: {}"


def ast_eq(expect, actual):
    assert expect == actual


def ast_ne(expect, actual):
    assert expect != actual


def ast_gt(expect, actual):
    assert actual > expect


def ast_lt(expect, actual):
    assert actual < expect


def ast_ge(expect, actual):
    assert actual >= expect


def ast_le(expect, actual):
    assert actual <= expect


def ast_in(expect, actual):
    """ 断言实际结果是否在期望结果中"""
    assert actual in expect


def ast_expect_in_actual(expect: list, actual):
    """ 断言期望结果是否在实际结果中"""
    for item in expect:
        assert item in actual


def ast_actual_in_expect(expect, actual: list):
    """ 断言实际结果是否在期望结果中"""
    for item in actual:
        assert item in expect


def ast_expect_ni_actual(expect, actual: list):
    """ 断言期望结果是否不存在实际结果中"""
    for item in expect:
        assert item not in actual


def ast_ni(expect, actual):
    assert actual not in expect


def ast_len(expect, actual):
    if actual is None:
        assert False, UNSUPPORTED.format(None)
    for ast_type in expect:
        doast = astdict.setdefault(ast_type, False)
        if doast:
            doast(expect[ast_type], len(actual))
        else:
            assert False, UNSUPPORTED.format(ast_type)


astdict = {"eq": ast_eq,
           "neq": ast_ne,
           "gt": ast_gt,
           "lt": ast_lt,
           "ge": ast_ge,
           "le": ast_le,
           "in": ast_in,
           "ni": ast_ni,
           "len": ast_len,
           "e_in_a": ast_expect_in_actual,
           "a_in_e": ast_actual_in_expect,
           "e_ni_a": ast_expect_ni_actual
           }


def ast(current, expects, response, fixture):
    if type(expects) != dict:
        assert False, "请检查xmind"
    for rp in response:
        content_type = rp[0].headers.get("content-type", "").split(";")
        assert "application/json" in content_type, "NOT JSON"
        body = jsl(str(rp[0].data, encoding="utf-8"))
        status = rp[1]
        headers = rp[2]
        # print("\nExpects: ", expects, "\nActual: ", body, status, headers)
        ast_body(expects.get("body"), body, fixture)
        ast_status(expects.get("status"), status, fixture)
        ast_headers(expects.get("headers"), headers, fixture)
        ast_rear(current, expects.get("rear"), fixture)


def ast_headers(expects, headers, fixture):
    if not expects:
        return
    for expect in expects:
        for ast_type in expects[expect]:
            doast = astdict.get(ast_type)
            if doast:
                doast(expects[ast_type], headers.get(expect))


def ast_status(expects, status, fixture):
    if not expects:
        return
    for ast_type in expects:
        doast = astdict.get(ast_type)
        if doast:
            doast(expects[ast_type], status)


def ast_body(expects, response, fixture):
    print("Expects :", expects, "Response :", jsd(
        response, indent=4, ensure_ascii=False))
    if not expects:
        return
    for expect in expects:
        actual = jmespath.search(str(expect), response)
        for ast_type in expects[expect]:
            doast = astdict.setdefault(ast_type, False)
            if doast:
                doast(expects[expect][ast_type], actual)
            else:
                assert False, UNSUPPORTED.format(ast_type)


def ast_rear(current, expects, fixture):
    if not expects:
        return
    pretreator = Pretreator()
    for casekey in expects:
        kwargs = expects[casekey].get("kwargs", {})
        for k, v in kwargs.items():
            kwargs[k] = prt(casekey, v[0], fixture)if isinstance(
                v[0], dict)else v.pop()
        rshs = pretreator.getrsh(current, f'test_{casekey}', kwargs, fixture)
        sub_expects = {expect: expects[casekey].get(expect) for expect in [
            "body", "status", "headers", "rear"]}
        ast(current, sub_expects, [[r[0] for r in rshs]], fixture)
