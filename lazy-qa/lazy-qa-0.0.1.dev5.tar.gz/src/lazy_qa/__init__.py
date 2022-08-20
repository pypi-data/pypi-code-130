__version__ = '0.0.0'
try:
    from ._lazy_qa import longest  # noqa
except ImportError:
    def longest(args):
        return max(args, key=len)
