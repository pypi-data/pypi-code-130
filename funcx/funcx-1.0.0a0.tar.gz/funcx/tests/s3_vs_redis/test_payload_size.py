import pytest

from funcx.utils.errors import TaskPending


def large_result_producer(size) -> str:
    return bytearray(size)


def wait_for_task(fxc, task_id, walltime: int = 10):
    import time

    start = time.time()
    while True:
        if time.time() > start + walltime:
            raise Exception("Timeout")
        try:
            r = fxc.get_result(task_id)
        except TaskPending:
            print("Not available yet")
            time.sleep(20)
        else:
            return r


test_cases = [1000, 15000, 18000, 19000, 20000, 21000]


@pytest.mark.parametrize("size", test_cases)
def test_allowed_arg_payloads(fxc, endpoint, size):
    """ funcX should allow all listed payloads which are under 512KB limit
    """
    fn_uuid = fxc.register_function(
        large_result_producer, endpoint, description="LargeResultProducer"
    )

    task_id = fxc.run(
        bytearray(size),  # This is the current result size limit
        endpoint_id=endpoint,
        function_id=fn_uuid,
    )

    x = wait_for_task(fxc, task_id, walltime=60)
    assert len(x) == size, "Wrong result length reported"


@pytest.mark.parametrize("size", test_cases)
def test_allowed_arg_payloads_executor(fx, endpoint, size):
    """ funcX should allow all listed payloads which are under 512KB limit
    """

    future = fx.submit(large_result_producer, size, endpoint_id=endpoint)
    x = future.result()
    assert len(x) == size, "Wrong result length reported"
