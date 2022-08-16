import pytest
from nosop_py import NosoNodeInfo

@pytest.fixture
def elements():
    return [
        'NODESTATUS', # Ignore
        3,            # Peers
        1024,         # Block
        0,            # Pending
        0,            # Sync Delta
        'BRANCH',     # Branch
        'Version',    # Version

        0,            # Time
        'MN_HASH',    # MN Hash
        0,            # MN count
        'LBHash',     # Last Block Hash
        'BHDiff',     # Best Hash Diff
        0,            # Last Block Time End
        'BHMiner',    # Best Hash Miner
        0,            # Checks count
        'LBPoW',      # Last Block PoW
        'LBDiff',     # Last Block Diff
        'SUMMARY',    # Summary
        'GVTs',       # GVTs
        'CFGs',       # CFGs
    ]

def test_NosoNodeInfo_no_args():
    ni = NosoNodeInfo()

    assert ni.peers == -1
    assert ni.block == -1
    assert ni.pending == -1
    assert ni.sync_delta == -1
    assert ni.branch == 'NONE'
    assert ni.version == 'UNKNOWN'

    assert ni.time == -1
    assert ni.mn_hash == 'UNKNOWN'
    assert ni.mn_count == -1
    assert ni.last_block_hash == 'UNKNOWN'
    assert ni.best_hash_diff == 'UNKNOWN'
    assert ni.last_block_time_end == -1
    assert ni.last_best_hash_miner == 'UNKNOWN'
    assert ni.checks_count == -1
    assert ni.last_block_pow == 'UNKNOWN'
    assert ni.last_block_diff == 'UNKNOWN'
    assert ni.summary == 'UNKNOWN'
    assert ni.gvts == 'UNKNOWN'
    assert ni.cfgs == 'UNKNOWN'



def test_NosoNodeInfo_with_args(elements):
    ni = NosoNodeInfo(*elements)

    assert ni.peers == 3
    assert ni.block == 1024
    assert ni.pending == 0
    assert ni.sync_delta == 0
    assert ni.branch == 'BRANCH'
    assert ni.version == 'Version'

    assert ni.time == 0
    assert ni.mn_hash == 'MN_HASH'
    assert ni.mn_count == 0
    assert ni.last_block_hash == 'LBHash'
    assert ni.best_hash_diff == 'BHDiff'
    assert ni.last_block_time_end == 0
    assert ni.last_best_hash_miner == 'BHMiner'
    assert ni.checks_count == 0
    assert ni.last_block_pow == 'LBPoW'
    assert ni.last_block_diff == 'LBDiff'
    assert ni.summary == 'SUMMARY'
    assert ni.gvts == 'GVTs'
    assert ni.cfgs == 'CFGs'
