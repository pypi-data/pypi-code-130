import pytest

from funcx.utils.errors import TaskPending


def large_result_consumer(data) -> str:
    return len(data)


def wait_for_task(fxc, task_id, walltime: int = 2):
    import time

    start = time.time()
    while True:
        if time.time() > start + walltime:
            raise Exception("Timeout")
        try:
            r = fxc.get_result(task_id)
        except TaskPending:
            print("Not available yet")
            time.sleep(1)
        else:
            return r


test_cases = [4500, 45000, 450000]


@pytest.mark.parametrize("size", test_cases)
def test_allowed_arg_payloads(fxc, endpoint, size):
    """ funcX should allow all listed payloads which are under 512KB limit
    """
    fn_uuid = fxc.register_function(
        large_result_consumer, endpoint, description="ResultConsumer"
    )

    task_id = fxc.run(
        bytearray(size),  # This is the current result size limit
        endpoint_id=endpoint,
        function_id=fn_uuid,
    )

    x = wait_for_task(fxc, task_id, walltime=10)
    assert x == size, "Wrong payload length reported"


def test_payload_too_large(fxc, endpoint, size=550000):
    """ funcX should be blocking this test because the function payload is too large.
    This doesn't work right now
    """

    fn_uuid = fxc.register_function(
        large_result_consumer, endpoint, description="ResultConsumer"
    )

    task_id = fxc.run(
        bytearray(size),  # This is the current result size limit
        endpoint_id=endpoint,
        function_id=fn_uuid,
    )

    # funcX should be raising an exception here
    x = wait_for_task(fxc, task_id, walltime=10)
    assert x == size, "Wrong payload length reported"
