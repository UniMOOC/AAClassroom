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

""" Badges module
    This module enables the posbility to issue badges
    with OpenBadges platform.
    config.yaml contains de API configuration.
"""


from models import custom_modules
from .handlers import SendBadgesHandler


def register_module():
    """Registers this module in the registry."""

    global_urls = [(
        '/script/sendBadges', SendBadgesHandler)]

    course_urls = []

    global custom_module
    custom_module = custom_modules.Module(
        'Module Badges',
        'Module to expose and manage badges and his service',
        global_urls, course_urls)
    return custom_module
