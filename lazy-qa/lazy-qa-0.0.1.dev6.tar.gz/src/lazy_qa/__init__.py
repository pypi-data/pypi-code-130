__version__ = '0.0.1'
try:
    from ._lazy_qa import longest  # noqa
except ImportError:
    def longest(args):
        return max(args, key=len)
