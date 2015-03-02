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

from models import custom_modules

from modules.um_sendgrid.controller import sendgridHandler

custom_module = None


def register_module():
    """Registers this module in the registry."""

    global_handlers = [
        ('/script/sendgrid/send', sendgridHandler)
    ]

    course_handlers = []

    global custom_module
    custom_module = custom_modules.Module(
        'Sendgrid email integration',
        '',
        global_handlers, course_handlers)

    return custom_module
