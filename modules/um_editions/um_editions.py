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

""" Editions module
    This module allows you to configure different editions for
    your courses.
"""
from models import custom_modules
from models.roles import Roles, Permission

from modules.um_editions import handlers


# This permission grants the user access to the i18n dashboard and console.
ACCESS_PERMISSION = 'access_editions_dashboard'
ACCESS_PERMISSION_DESCRIPTION = 'Can access Editions Dashboard.'


def register_module():
    """Registers this module in the registry."""

    global_urls = []
    course_urls = [
        ('/api/editions', handlers.EditionsAPIHandler)
    ]

    global custom_module
    custom_module = custom_modules.Module(
        'Editions',
        'Different instances of the same course.',
        global_urls, course_urls)

    register_roles_permissions(custom_module)

    return custom_module


def register_roles_permissions(custom_module):
    Roles.register_permissions(custom_module, permissions_callback)


def permissions_callback(unused_app_context):
    return [
        Permission(ACCESS_PERMISSION, ACCESS_PERMISSION_DESCRIPTION),
    ]
