"""Library components."""

from robotlibcore import keyword


class Library1(object):

    @keyword
    def example(self):
        """Keyword documentation."""
        pass

    @keyword
    def another_example(self, arg1, arg2='default'):
        pass

    def not_keyword(self):
        pass


class Library2(object):

    @keyword('Custom name')
    def this_name_is_not_used(self):
        pass

    @keyword(tags=['tag', 'another'])
    def tags(self):
        pass
