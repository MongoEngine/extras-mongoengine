try:
    import unittest2 as unittest
except ImportError:
    import unittest

from enum import Enum

class IntEnum(Enum):
    FIRST = 1
    SECOND = 2

class StringEnum(Enum):
    FIRST = 'FIRST'
    SECOND = 'SECOND'

from mongoengine import Document, connect, connection
from extras_mongoengine.fields import StringEnumField, IntEnumField


class EnumFieldTestCase(unittest.TestCase):

    def setUp(self):
        connect(db='extrasmongoenginetest')
        self.db = connection.get_db()

        class Doc(Document):
            string_enum = StringEnumField(StringEnum, default=StringEnum.FIRST)
            int_enum = IntEnumField(IntEnum, default=IntEnum.FIRST)
        self.document_class = Doc
        self.doc = self.document_class()
        self.doc.save()

    def tearDown(self):
        for collection in self.db.collection_names():
            if 'system.' in collection:
                continue
            self.db.drop_collection(collection)

    def test_creation(self):
        self.assertTrue(self.doc.string_enum is StringEnum.FIRST)
        self.assertTrue(self.doc.int_enum is IntEnum.FIRST)

    def test_read(self):
        doc = self.document_class.objects.first()
        self.assertTrue(doc.string_enum is StringEnum.FIRST)
        self.assertTrue(doc.int_enum is IntEnum.FIRST)

    def test_write_and_read(self):
        doc = self.document_class.objects.first()
        doc.string_enum = StringEnum.SECOND
        doc.int_enum = IntEnum.SECOND
        doc.save()
        self.assertTrue(doc.string_enum is StringEnum.SECOND)
        self.assertTrue(doc.int_enum is IntEnum.SECOND)

        doc = self.document_class.objects.first()
        self.assertTrue(doc.string_enum is StringEnum.SECOND)
        self.assertTrue(doc.int_enum is IntEnum.SECOND)


if __name__ == '__main__':
    unittest.main()
