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
from modules.um_common.handlers import UMBaseHandler
from modules.um_common.utils import is_super_admin


class AdminManagerHandler(UMBaseHandler):

    @is_super_admin
    def get(self):
        self.personalize_page_and_get_user()
        self.template_value['base_url'] = self.get_base_href(self)
        self.render('modules/um_course/views/admin.html')
