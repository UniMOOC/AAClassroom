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

from modules.aecommon.controllers.base import AEBaseHandler
from modules.um_sendgrid.service import SendGrid


class sendgridHandler(AEBaseHandler):

    def post(self):
        from_adr = self.request.get('from_adr')
        to_adr = self.request.get('to_adr')
        subject = self.request.get('subject')
        body = self.request.get('body')
        template_id = self.request.get('template_id')

        subs_json = self.request.get('substitutions')
        substitutions = json.loads(subs_json) if subs_json else None

        cat_json = self.request.get('categories')
        categories = json.loads(cat_json) if cat_json else None

        SendGrid.send_email(
            from_adr, to_adr, subject, body,
            template_id, substitutions, categories
        )

        self.response.status_int = 201
        self.response.out.write("OK")
