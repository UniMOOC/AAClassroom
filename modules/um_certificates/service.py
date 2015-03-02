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
from modules.um_badges.service import Badges
from .model import AssessmentCertificateDAO


class AssessmentCertificates(object):
    """ Class to manage certificates in app

        A certificate is badge and a list of assessments related to
        issue badge for assessment. The student must to pass all
        assessments in certificate to get the badge.

        Also, the certificate can have an start_date and end_date
        that limit the issue process between this dates.

        A certificate is considerated active when date.now() is between
        the start and end date.

        It could be posible be null any of both properties.

        The most common use to this class is issue_certificates_by_assessment.
    """

    @classmethod
    def get_actives_by_assessment_in_edition(cls, asm_id, edition):
        return AssessmentCertificateDAO.\
            get_actives_by_assessment_in_edition_or_default(asm_id, edition)

    @classmethod
    def issue_certificates_by_assessment(
            cls, student, asm_id, edition):
        """ Issue certificates for assessment if it has to.

            The function gets the certificates that are active and have
            an assessment passed in asm_id. Then iterates over them
            and issues the badge for the student if the student
            has passed all assessments in the certificate (when the certificate
            requieres to do so).

            The badge is sended to the mail
            student.additional_feilds['acreditation_email']
            and name student.name.

            Parameters:
            - student: Student object with the student to issue badges
            - asm_id: String with assessment identifier.
            - edition: Edition related with the certificate.

            Returns:
            - List with certificates issueds
        """
        issueds = []
        certs = cls.get_actives_by_assessment_in_edition(asm_id, edition)
        for cert in certs:
            if cert.badge and cls.student_can_get_certificate(student, cert):
                    Badges.give_badge_to_student(
                        student, cert.badge)
                    issueds.append(cert.badge)
        return issueds

    @classmethod
    def student_can_get_certificate(cls, student, cert):
        """ Test if a student can get the certificate.

            Calls to Student service to test if all assessments
            in certificate has passed. If any of them is not passed
            return False.

            Parameters:
            - student: Student object to test.
            - cert: AssessmentCertificate object to test.

            Returns:
            - Boolean: If student can get the certificate.
        """
        for asm_id in cert.assessments:
            if cert.requires_passing:
                if not student.is_assessment_pass(asm_id):
                    return False
            else:
                if not student.has_attempted_assessment(asm_id):
                    return False
        return True

    @classmethod
    def create(cls, edition, assessments, badge_id, date_start,
               date_end, requires_passing):
        AssessmentCertificateDAO.create(
            badge_id, assessments, edition, date_start,
            date_end, requires_passing)

    @classmethod
    def get_by_id(cls, badge_id):
        return AssessmentCertificateDAO.get_by_id(badge_id)
