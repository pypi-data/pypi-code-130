from .myhttp.logging import *
from typing import Callable, Any, Dict

TestFunction = Callable[[Any], bool]
testActions = []

class TestAction:
    def __init__(self, f:Callable, params:Dict[str, Any], expects:bool):
        self.name = f.__name__
        self.action = lambda: f.__call__(**params) == expects

    def __call__(self) -> bool:
        return self.action()

def test(params:Dict[str, Any], expects:bool) -> TestFunction:
    def inner(f:TestFunction) -> TestFunction:
        testActions.append(TestAction(f, params, expects))
        return f
    return inner

def run_test():
    tests = len(testActions)
    success = 0
    while len(testActions) > 0:
        t = testActions.pop()
        badge_async(t.name, LogColors.DARK_BACKGROUND_BLACK, 'testing', LogColors.DARK_BACKGROUND_YELLOW, False)
        if t():
            badge_async(t.name, LogColors.DARK_BACKGROUND_BLACK, 'passed', LogColors.DARK_BACKGROUND_GREEN)
            success += 1
        else:
            badge_async(t.name, LogColors.DARK_BACKGROUND_BLACK, 'failed', LogColors.DARK_BACKGROUND_RED)

    badge_async(str(tests), LogColors.DARK_BACKGROUND_BLACK, 'test cases :', LogColors.DARK_BACKGROUND_BLUE, padding=False)
    badge_async(str(success), LogColors.DARK_BACKGROUND_BLACK, 'test passed:', LogColors.DARK_BACKGROUND_GREEN, padding=False)
    badge_async(str(tests - success), LogColors.DARK_BACKGROUND_BLACK, 'test failed:', LogColors.DARK_BACKGROUND_RED, padding=False)
 