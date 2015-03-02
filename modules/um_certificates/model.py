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
import datetime

from google.appengine.ext import db

from models.models import MemcacheManager


class AssessmentCertificate(db.Model):
    """ Class to store relations between badges and assessments.

        The id is managed by autocreted key().id().
        See AssessmentCertificates service in service file to
        get more information.
    """
    badge_id = db.StringProperty()
    assessments = db.StringListProperty()
    date_start = db.DateTimeProperty(auto_now_add=True)
    date_end = db.DateTimeProperty()
    edition = db.StringProperty()
    requires_passing = db.BooleanProperty(default=True)


class AssessmentCertificateDTO(object):
    """ DTO de AssessmentCertificate that extends some functionality.

        Stores the id in key_id property get it by AssessmentCertificate
        key().id() property.
    """
    def __init__(self, assessment_certificate=None):
        if assessment_certificate:
            self.key_id = assessment_certificate.key().id()
            self.badge = assessment_certificate.badge_id
            self.assessments = assessment_certificate.assessments
            self.date_start = assessment_certificate.date_start
            self.date_end = assessment_certificate.date_end
            self.edition = assessment_certificate.edition
            self.requires_passing = assessment_certificate.requires_passing

    def is_active(self):
        """ Test if actual date if between dates in certificate """
        date = self.get_now()
        return ((not self.date_start or self.date_start <= date) and
                (not self.date_end or self.date_end >= date))

    def get_now(self):
        """ Get the actual datetime """
        return datetime.datetime.now()


class AssessmentCertificateDAO(object):
    """ Manage AssessmentCertificate model.

        Stores and get entities transformed to DTO.
        All the date is stored in cache in key:
            CERTIFICATES_MEMCACHE_KEY + edition
        All functions returned de model transformed to DTO.
    """
    CERTIFICATES_MEMCACHE_KEY = 'assessment-certificates-'
    CERTIFICATES_EDITION_DEFAULT = 'default'

    @classmethod
    def create(cls, badge_id, assessments, edition,
               date_start=None, date_end=None, requires_passing=True):
        cert = AssessmentCertificate(
            badge_id=badge_id,
            assessments=assessments,
            edition=edition,
            date_start=date_start,
            date_end=date_end,
            requires_passing=requires_passing)
        cert.put()
        return AssessmentCertificateDTO(cert)

    @classmethod
    def set(cls, cert_dto):
        cert = AssessmentCertificate.get_by_id(cert_dto.key_id)
        if cert:
            cert.badge_id = cert_dto.badge
            cert.assessments = cert_dto.assessments
            cert.date_start = cert_dto.date_start
            cert.date_end = cert_dto.date_end
            cert.edition = cert_dto.edition
            cert.requires_passing = cert_dto.requires_passing
            cert.put()
            return AssessmentCertificateDTO(cert)

    @classmethod
    def _all_in_edition(cls, edition):
        certificates = AssessmentCertificate.all()
        certificates = certificates.filter('edition', edition)
        return [AssessmentCertificateDTO(certificate)
                for certificate in certificates]

    @classmethod
    def _memcache_key(cls, edition):
        return cls.CERTIFICATES_MEMCACHE_KEY + edition

    @classmethod
    def all_in_edition_or_default(cls, edition):
        """ Gets certificates in edition edition and edition none """
        def_certificates = cls.all_in_edition(
            cls.CERTIFICATES_EDITION_DEFAULT)
        edi_certificates = cls.all_in_edition(edition)
        return def_certificates + edi_certificates

    @classmethod
    def all_in_edition(cls, edition):
        certificates = MemcacheManager.get(
            cls._memcache_key(edition))
        if not certificates:
            certificates = cls.refresh_certificates_in_edition(edition)
        return certificates

    @classmethod
    def get_actives_in_edition(cls, edition):
        certificates = cls.all_in_edition(edition)

        certificates_actives = [certificate for certificate in certificates
                                if certificate.is_active()]
        return certificates_actives

    @classmethod
    def get_by_assessment_in_edition(cls, asm_id, edition):
        certificates = cls.all_in_edition(edition)

        certificates_actives = [certificate for certificate in certificates
                                if asm_id in certificate.assessments]
        return certificates_actives

    @classmethod
    def get_actives_by_assessment_in_edition_or_default(cls, asm_id, edition):
        certificates = cls.all_in_edition_or_default(edition)

        certificates_actives = [certificate for certificate in certificates
                                if asm_id in certificate.assessments
                                and certificate.is_active()]
        return certificates_actives

    @classmethod
    def get_actives_by_assessment_in_edition(cls, asm_id, edition):
        certificates = cls.all_in_edition(edition)

        certificates_actives = [certificate for certificate in certificates
                                if asm_id in certificate.assessments
                                and certificate.is_active()]
        return certificates_actives

    @classmethod
    def refresh_certificates_in_edition(cls, edition):
        certificates = cls._all_in_edition(edition)
        MemcacheManager.set(
            cls._memcache_key(edition), certificates)
        return certificates

    @classmethod
    def get_by_id(cls, badge_id):
        certs = cls.all_in_edition(cls.CERTIFICATES_EDITION_DEFAULT)
        return [cert for cert in certs if cert.badge == badge_id]
