
PY_HEADER = """# Copyright 2015 UniMOOC. All Rights Reserved.
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

"""


def main():

    files = [
        "./modules/um_admin_manager/um_admin_manager.py",
        "./modules/um_admin_manager/handlers.py",
        "./modules/um_assessments/handlers.py",
        "./modules/um_assessments/service.py",
        "./modules/um_assessments/um_assessments.py",
        "./modules/um_assessments/model.py",
        "./modules/um_assessments/exceptions.py",
        "./modules/um_badges/um_badges.py",
        "./modules/um_badges/handlers.py",
        "./modules/um_badges/service.py",
        "./modules/um_badges/model.py",
        "./modules/um_certificates/um_certificates.py",
        "./modules/um_certificates/handlers.py",
        "./modules/um_certificates/service.py",
        "./modules/um_certificates/model.py",
        "./modules/um_common/handlers.py",
        "./modules/um_common/service.py",
        "./modules/um_common/tools.py",
        "./modules/um_common/utils.py",
        "./modules/um_course/handlers.py",
        "./modules/um_course/service.py",
        "./modules/um_course/um_course.py",
        "./modules/um_course_api/um_course_api.py",
        "./modules/um_course_api/handlers.py",
        "./modules/um_course_api/services.py",
        "./modules/um_course_api/serializers.py",
        "./modules/um_course_api/exceptions.py",
        "./modules/um_course_api/api_models.py",
        "./modules/um_editions/um_editions.py",
        "./modules/um_editions/handlers.py",
        "./modules/um_editions/service.py",
        "./modules/um_editions/model.py",
        "./modules/um_editions/exceptions.py",
        "./modules/um_gobalo/service.py",
        "./modules/um_sendgrid/um_sendgrid.py",
        "./modules/um_sendgrid/service.py",
        "./modules/um_sendgrid/controller.py",
        "./modules/um_students/um_students.py",
        "./modules/um_students/mixin.py",
        "./modules/um_students/handlers.py",
        "./modules/um_students/service.py",
        "./modules/um_students/model.py",
        "./modules/um_students/exceptions.py",
        "./modules/um_students/utils.py"
    ]

    for line in files:
        if '__init__' not in line:
            f = open(line, 'r+w')
            content = PY_HEADER.rstrip('\r\n') + '\n' + f.read()
            f.seek(0, 0)
            f.write(content)
            f.close()


if __name__ == '__main__':
    main()
