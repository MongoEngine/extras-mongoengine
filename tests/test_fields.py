try:
    import unittest2 as unittest
except ImportError:
    import unittest
from datetime import timedelta
from mongoengine import Document, NotUniqueError, ValidationError, connect
from mongoengine.connection import get_db

from extras_mongoengine.fields import TimedeltaField, LowerStringField, LowerEmailField


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

class LowerStringFieldTestCase(unittest.TestCase):

    def setUp(self):
        connect(db='extrasmongoenginetest')
        self.db = get_db()

    def tearDown(self):
        for collection in self.db.collection_names():
            if 'system.' in collection:
                continue
            self.db.drop_collection(collection)

    def test_case_insensitive_querying(self):
        class BlogPost(Document):
            slug = LowerStringField()

        BlogPost.objects.create(slug='whatever')
        self.assertEqual(BlogPost.objects.get(slug='WHATEVER').slug, 'whatever')

    def test_case_insensitive_uniqueness(self):
        class User(Document):
            username = LowerStringField(unique=True)

        User.objects.create(username='whatever')
        dupe = User(username='WHATEVER')
        self.assertRaises(NotUniqueError, dupe.save)

    def test_lower_email_validation(self):
        class User(Document):
            email = LowerEmailField()

        u = User.objects.create(email='test@example.com')
        self.assertEqual(User.objects.get(email='Test@EXAMPLE.COM'), u)

        u2 = User(email='whatever')
        self.assertRaises(ValidationError, u2.save)


if __name__ == '__main__':
    unittest.main()
