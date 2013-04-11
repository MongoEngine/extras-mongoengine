import unittest2 as unittest
from datetime import timedelta
from fields import TimedeltaField

class OldStyleTimedelta(timedelta):
    "Used for backwards compatibility testing"
    def total_seconds(self):
        raise AttributeError

class TimedeltaFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = TimedeltaField()

    def test_construct(self):
        self.assertIsInstance(self.field, TimedeltaField)

    def test_total_seconds(self):
        value = timedelta(minutes=1, seconds=10)
        self.assertEqual(self.field.total_seconds(value), 70)

    def test_total_seconds_26(self):
        value = OldStyleTimedelta(minutes=1, seconds=10)
        self.assertEqual(self.field.total_seconds(value), 70)

if __name__ == '__main__':
    unittest.main()
