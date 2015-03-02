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

import appengine_config
from common import jinja_utils
from controllers.utils import BaseHandler


DIR = appengine_config.BUNDLE_ROOT


class UMBaseHandler(BaseHandler):
    def render(self, template_file, template_dir=''):
        dirs = [template_dir, DIR] if template_dir else DIR
        template = jinja_utils.get_template(template_file, dirs)
        self.response.write(template.render(self.template_value))

    def write_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(obj, default=lambda o: o.__dict__))

    def return_with_error(self, code, message):
        self.response.out.write(message)
        self.response.status = code
