import os
import datetime

from mongoengine.base import BaseField
from mongoengine.python_support import str_types

from django.db.models.fields.files import FieldFile
from django.core.files.base import File
from django.core.files.storage import default_storage

from django.utils.encoding import force_str, force_text


class LocalStorageFileField(BaseField):

    proxy_class = FieldFile

    def __init__(self,
                 size=None,
                 name=None,
                 upload_to='',
                 storage=None,
                 **kwargs):
        self.size = size
        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to
        super(LocalStorageFileField, self).__init__(**kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        file = instance._data.get(self.name)

        if isinstance(file, str_types) or file is None:
            attr = self.proxy_class(instance, self, file)
            instance._data[self.name] = attr

        return instance._data[self.name]

    def __set__(self, instance, value):
        key = self.name
        if isinstance(value, File) and not isinstance(value, FieldFile):
            file = instance._data.get(self.name)
            if file:
                try:
                    file.delete()
                except:
                    pass
            # Create a new proxy object as we don't already have one
            file_copy = self.proxy_class(instance, self, value.name)
            file_copy.file = value
            instance._data[key] = file_copy
        else:
            instance._data[key] = value

        instance._mark_as_changed(key)

    def get_directory_name(self):
        return os.path.normpath(force_text(
                datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(
                self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(
                self.get_directory_name(), self.get_filename(filename))

    def to_mongo(self, value):
        if isinstance(value, self.proxy_class):
            return value.name
        return value
