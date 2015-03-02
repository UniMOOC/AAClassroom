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

import dateutil.parser
from lib.pytz.gae import pytz
import yaml

from google.appengine.api import users


def get_month_name(month_no, locale):
    """with TimeEncoding(locale) as encoding:
        s = month_name[month_no]
        if encoding is not None:
            s = s.decode(encoding)
        return s"""
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
        "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    return months[int(month_no) - 1]


class FakeModule(object):
    """ A Fake version of GCB Module
        Used to call functions that require the global module variable
        in places where it's absurd to have access to that variable.
    """

    def __init__(self, name):
        self.name = name


class FakeUser(object):
    """ A Fake AppEngine user model
    """

    def __init__(self, email, user_id):
        self._email = email
        self._user_id = user_id

    def email(self):
        return self._email

    def user_id(self):
        return self._user_id


class ConfigReader(object):
    _config_file = ''
    _config = None

    def __init__(self, config_file):
        self._config_file = config_file

    def __getitem__(self, key):
        if self._config is None:
            self._config = yaml.load(open(self._config_file))

        return self._config[key]


def is_super_admin(fn):
    """ Decorator that checks if the current user is a super admin
    """
    def inner_fn(handler, *unused_args, **unused_kwargs):
        from modules.um_course.service import Courses
        user = users.get_current_user()
        if not user:
            handler.redirect(
                users.create_login_url(handler.request.uri), normalize=False
            )
            return None
        if not Courses.is_course_admin(user.email()):
            handler.abort(403)
        return fn(handler, *unused_args, **unused_kwargs)
    return inner_fn


class TimeHelper(object):
    _utc = pytz.utc
    _europe_madrid = pytz.timezone('Europe/Madrid')

    @classmethod
    def to_GMT1(cls, date):
        if not date.tzinfo:
            date = cls._utc.localize(date)
        gmt1_dt = date.astimezone(cls._europe_madrid)
        return gmt1_dt

    @classmethod
    def from_GMT1(cls, date):
        if not date.tzinfo:
            date = cls._europe_madrid.localize(date)
        utc_dt = date.astimezone(cls._utc)
        return utc_dt

    @classmethod
    def from_isoformat(cls, date_string):
        return dateutil.parser.parse(date_string)


def mix_in(base, addition):
    """Mixes in place, i.e. the base class is modified.
    Tags the class with a list of names of mixed members.
    """
    mixed = []
    for item, val in addition.__dict__.items():
        if not hasattr(base, item):
            setattr(base, item, val)
            mixed.append(item)
    base._mixed_ = mixed
