import os


# -------------------
def pytest_addoption(parser):
    parser.addoption('--iuvmode', action='store_true', dest='iuvmode', default=False)


# -------------------
def pytest_configure(config):
    os.environ['iuvmode'] = str(config.getoption('iuvmode'))
