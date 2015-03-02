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

import urllib2
import json
import datetime
import appengine_config
from google.appengine.api.app_identity import get_application_id

from modules.um_common.utils import ConfigReader


class GobaloAPI(object):
    config = ConfigReader('modules/um_gobalo/config.yaml')

    @classmethod
    def get_user_info(cls, email):
        user_info_endpoint = cls.config['endpoints']['user_info']

        try:
            r = urllib2.urlopen(user_info_endpoint.format(email))
            res = json.loads(r.read())
            return res['nombre'], res['apellidos'], res['evento_nombre']
        except:
            return None, None, None

    @classmethod
    def user_attended(cls, email, date):
        attended_endpoint = cls.config['endpoints']['user_attended']

        formated_date = date.strftime('%Y-%m-%d')
        try:
            r = urllib2.urlopen(attended_endpoint.format(formated_date, email))
            res = json.loads(r.read())
            if res[0]['result']:
                return 'ATTENDED'
            else:
                return 'TOO_MANY_MISSES'
        except Exception as ex:
            import logging
            logging.error(str(ex))
            return 'DIDNT_ATTEND'

    @classmethod
    def user_attended_today(cls, email):
        date = datetime.datetime.utcnow()
        return cls.user_attended(email, date)


if (not appengine_config.PRODUCTION_MODE
        or get_application_id() == 'devaaclassroom2015'):
    @classmethod
    def mock_get_user_info(cls, email):
        return 'Potato', 'Tomato', 'md-bas-madrid-03'

    @classmethod
    def mock_user_attended(cls, email, date):
        return 'ATTENDED'

    GobaloAPI.get_user_info = mock_get_user_info
    GobaloAPI.user_attended = mock_user_attended
