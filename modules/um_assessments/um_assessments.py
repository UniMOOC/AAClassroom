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

""" Assessments module
    This module handles the configuration of limited attempts to
    pass an assessment as well as the dates in which you can try
    to do them.
"""


from models import custom_modules
from modules.um_assessments import handlers


def register_module():
    """Registers this module in the registry."""

    global_urls = []
    course_urls = [
        ('/api/assessment', handlers.AsmAPIHandler),
        ('/api/assessment/dates', handlers.AsmDatesAPIHandler),
        ('/api/assessment/dates/_bulk', handlers.AsmDatesBulkAPIHandler),
        ('/api/student/attempts', handlers.AsmAttemptsAPIHandler),
        ('/api/extra-attempts', handlers.ExtraAttemptAPIHandler),
        ('/api/student/extra-attempts', handlers.StudentExtraAttemptAPIHandler)
    ]

    global custom_module
    custom_module = custom_modules.Module(
        'Assessments',
        'Restrict the times a student can do an assessment.',
        global_urls, course_urls)
    return custom_module
