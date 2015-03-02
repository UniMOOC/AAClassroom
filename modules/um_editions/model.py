# Copyright 2015 UniMOOC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.ext import db

from .exceptions import *


class EditionModel(db.Model):
    name = db.StringProperty()
    users = db.ListProperty(str)


class EditionDTO(object):

    def __init__(self, edition):
        self.key = edition.key().name()
        self.name = edition.name
        self.users = edition.users


class EditionDAO(object):
    @classmethod
    def get(cls, key):
        model = cls._get_model(key)
        if model:
            return EditionDTO(model)

    @classmethod
    def create(cls, key, name):
        if cls._get_model(key):
            raise EditionAlreadyExists
        edition = EditionModel(key_name=key, name=name)
        edition.put()
        return EditionDTO(edition)

    @classmethod
    def _get_model(cls, key):
        return EditionModel.get_by_key_name(key)

    @classmethod
    def set(cls, dto):
        edition = cls._get_model(dto.key)
        edition.name = dto.name
        edition.users = dto.users
        edition.put()
