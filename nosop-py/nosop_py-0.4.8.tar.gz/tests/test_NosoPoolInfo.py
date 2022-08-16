import pytest
from nosop_py import NosoPoolInfo

@pytest.fixture
def elements():
    return [
        3,        # Miners Count
        1,        # Last Block Rate
        100,      # Pool Fee
        100,      # Main Net Hash Rate
    ]

def test_NosoPoolInfo_no_args():
    pi = NosoPoolInfo('TestPool')

    assert pi.name == 'TestPool'
    assert pi.miners_count == -1
    assert pi.last_block_rate == -1
    assert pi.pool_fee == -1
    assert pi.main_net_hash_rate == -1

def test_NosoPoolInfo_with_args(elements):
    pi = NosoPoolInfo('TestPool', *elements)

    assert pi.name == 'TestPool'
    assert pi.miners_count == 3
    assert pi.last_block_rate == 1
    assert pi.pool_fee == 100
    assert pi.main_net_hash_rate == 100
