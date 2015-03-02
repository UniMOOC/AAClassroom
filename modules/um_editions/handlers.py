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

from modules.um_common.utils import is_super_admin
from modules.um_common.utils import TimeHelper
from modules.um_course_api.handlers import BaseAPIHandler
from .service import Editions
from .model import EditionModel, EditionDTO


class EditionsAPIHandler(BaseAPIHandler):
    """ Handlers for /api/editions"""
    _MODEL_HANDLER = EditionModel
    _DTO_HANDLER = EditionDTO
    _ID_KEYS = ['name']

    @is_super_admin
    def post(self):
        edition_code = self.request.get('code')
        start_date = self.request.get('start_date')

        start_date = TimeHelper.from_isoformat(start_date)
        utc_date = TimeHelper.from_GMT1(start_date)

        Editions.create_edition(edition_code, utc_date)
