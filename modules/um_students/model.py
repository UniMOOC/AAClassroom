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
import json


class StudentAPISerializer(object):
    def __init__(self, student):
        self.name = self._getattr(student, 'name')
        self.email = self._getattr(student, 'email')
        self.scores = self._to_json(self._getattr(student, 'scores'))
        self.additional_fields = self._to_json(
            self._getattr(student, 'additional_fields'))

    def _getattr(self, obj, key):
        if hasattr(obj, key):
            return getattr(obj, key)
        else:
            return obj[key]

    def _to_json(self, obj):
        if obj and not type(obj) is dict:
            return json.loads(obj)
        return obj

    def to_student(self, user):
        user.name = self.additional_fields['name'] + ' ' +\
            self.additional_fields['last_name']
        if (self.scores):
            user.scores = json.dumps(self.scores)
        if self.additional_fields:
            user.additional_fields = json.dumps(self.additional_fields)
        return user
