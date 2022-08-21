from django import test


class TestCase(test.TestCase):
    def assertCount(self, klass, count, msg=None):
        self.assertEqual(klass.objects.count(), count, msg=None)
