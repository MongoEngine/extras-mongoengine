from datetime import timedelta
from mongoengine.base import BaseField
from mongoengine.fields import StringField, EmailField

import os
import datetime

from mongoengine.python_support import str_types
from django.db.models.fields.files import FieldFile
from django.core.files.base import File
from django.core.files.storage import default_storage

from mongoengine.connection import get_db, DEFAULT_CONNECTION_NAME
from django.utils.encoding import force_text


class TimedeltaField(BaseField):
    """A timedelta field.

    Looks to the outside world like a datatime.timedelta, but stores
    in the database as an integer (or float) number of seconds.

    """
    def validate(self, value):
        if not isinstance(value, (timedelta, int, float)):
            self.error(u'cannot parse timedelta "%r"' % value)

    def to_mongo(self, value):
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        return timedelta(seconds=value)

    def prepare_query_value(self, op, value):
        if value is None:
            return value
        if isinstance(value, timedelta):
            return self.total_seconds(value)
        if isinstance(value, (int, float)):
            return value

    @staticmethod
    def total_seconds(value):
        """Implements Python 2.7's datetime.timedelta.total_seconds()
        for backwards compatibility with Python 2.5 and 2.6.

        """
        try:
            return value.total_seconds()
        except AttributeError:
            return (value.days * 24 * 3600) + \
                   (value.seconds) + \
                   (value.microseconds / 1000000.0)


class LocalStorageFileField(BaseField):

    proxy_class = FieldFile

    def __init__(self,
                 db_alias=DEFAULT_CONNECTION_NAME,
                 name=None,
                 upload_to='',
                 storage=None,
                 **kwargs):

        self.db_alias = db_alias
        self.storage = storage or default_storage
        self.upload_to = upload_to

        if callable(upload_to):
            self.generate_filename = upload_to

        super(DJFileField, self).__init__(**kwargs)


    def __get__(self, instance, owner):
        # Lots of information on whats going on here can be found
        # on Django's FieldFile implementation, go over to GitHub to
        # read it.
        file = instance._data.get(self.name)

        if isinstance(file, str_types) or file is None:
            attr = self.proxy_class(instance, self, file)
            instance._data[self.name] = attr

        elif isinstance(file, File) and not isinstance(file, FieldFile):
            file_copy = self.proxy_class(instance, self, file.name)
            file_copy.file = file
            file_copy._committed = False
            instance._data[self.name] = file_copy

        elif isinstance(file, FieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self
            file.storage = self.storage

        return instance._data[self.name]


    def __set__(self, instance, value):
        instance._data[self.name] = value


    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(self.upload_to)))


    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))


    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))


    def to_mongo(self, value):
    # Store the path in MongoDB
    # I also used this bit to actually save the file to disk.
    # The value I'm getting here is a FileFiled and it all looks ok.

        if not value._committed and value is not None:
            value.save(value.name, value)
            return value.path

        return value.name


    def to_python(self, value):
        eu = self
        return eu.proxy_class(eu.owner_document, eu, value)


class LowerStringField(StringField):
    def __set__(self, instance, value):
        value = self.to_python(value)
        return super(LowerStringField, self).__set__(instance, value)

    def to_python(self, value):
        if value:
            value = value.lower()
        return value

    def prepare_query_value(self, op, value):
        value = value.lower() if value else value
        return super(LowerStringField, self).prepare_query_value(op, value)


class LowerEmailField(LowerStringField):

    def validate(self, value):
        if not EmailField.EMAIL_REGEX.match(value):
            self.error('Invalid Mail-address: %s' % value)
        super(LowerEmailField, self).validate(value)

