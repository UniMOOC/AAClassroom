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
import re

from google.appengine.api import namespace_manager
from google.appengine.ext import deferred

from models.models import MemcacheManager

from modules.um_common.tools import UrlfetchHelper
from modules.um_common.utils import ConfigReader

from .model import SentBadgeDAO


class Badges():
    """ All relate function with Badges inside platform.

        Badge is an acreditation issue when you pass a assessments
        or maybe a few assessments or an assessment in a date, etc.
        For now thats use an external serice (OpenBadges) that allow
        issue badges throught an API.

        SentBadge is the relation between badge and student. Stores de info
        about the student date issued, badge issued and a status code showing
        how is the badge state in OpenBadges.
    """

    PENDING = 'PENDING'
    SENT = 'SENT'
    ALREADY_SENT = 'ALREADY_SENT'
    ERROR = 'ERROR'

    @classmethod
    def student_has_badge(cls, student_email, badge_id):
        """ Try if get SentBadge with email and badge is none """
        badge = SentBadgeDAO.get(
            user_email=student_email,
            badge_id=badge_id,
            single_record=True)
        return (badge is not None)

    @classmethod
    def get_badge_of_student(cls, student_email, badge_id):
        """ Get the SentBadgeDTO or none """
        badge = SentBadgeDAO.get(
            user_email=student_email,
            badge_id=badge_id,
            single_record=True)
        if badge:
            badge = badge.badge_id
        return badge

    @classmethod
    def get_mails_with_badge(cls, badge_id):
        """ Get a list of emails with de badge_id in SentBadges """
        emails = [sent_badge.user_email
                  for sent_badge in SentBadgeDAO.get(badge_id=badge_id)]
        return list(set(emails))

    @classmethod
    def get_pending(cls):
        """ Get the SentBadges with status PENDING """
        return SentBadgeDAO.get(status=cls.PENDING)

    @classmethod
    def get_badges_of_student(cls, student_email):
        """ Return a list of badge ids issued to a student """
        id_list = [s.badge_id
                   for s in SentBadgeDAO.get(user_email=student_email)]
        id_list = list(set(id_list))
        return id_list

    @classmethod
    def get_sent_badges_of_student(cls, student_email):
        """ Return array of SentBadgesDTO issued to a student """
        return SentBadgeDAO.get(user_email=student_email)

    @classmethod
    def give_badge_to_student(cls, student, badge_id):
        """ Give a badge to a student getting his name and email """
        cls.give_badge(
            student.acreditations_email(),
            student.complete_name(),
            badge_id)

    @classmethod
    def give_badge(cls, email, student_name, badge_id):
        """ Create a SentBadge and a task to issued via OpenBadges """
        if not cls.student_has_badge(email, badge_id):
            badge = SentBadgeDAO.create(
                email,
                student_name,
                badge_id)
            cls.deferred_send_badge(badge)

    @classmethod
    def deferred_send_badge(cls, sent_badge):
        """ Create a deferred task to issue a badge """
        deferred.defer(deferred_send_badge, sent_badge)

    @classmethod
    def get_badges_email(cls, student):
        return student.acreditations_email()


class OpenBadges(object):
    """ Service to comunicate to OpenBadges API

        This class have functionalities to issue badges via OpenBadges.
        To issue a badge you need an access_token to authenticate via
        Oauth2. This token is stored in Memcache but a 401 response from
        the API refresh it.

        To get the access token authorization credentials are getit from
        config.yaml.
            TODO: Get diferent credentials for diferents courses

        Easy use:
            Call get_token_and_send_badge() with a SentBadgeDTO
    """
    CONFIG = ConfigReader('modules/um_badges/config.yaml')
    _MEMCACHE_KEY = 'openbadges-token'

    @classmethod
    def get_token_and_send_badge(cls, sent_badge):
        """ Get an accest_token and issue the badge """
        token = cls.get_token_from_memcache()
        cls.send_badge(sent_badge, token)

    @classmethod
    def create_badge_url(cls, badge_id, user_email):
        config = cls.CONFIG['openbadges']
        return config['api_host'] + '/enterprise/claim/issactivate/' +\
            badge_id + '/' + user_email

    @classmethod
    def create_certificate_url(cls, certificate_id, user_email,
                               check_badge=False):
        if (not check_badge
                or Badges.student_has_badge(user_email, certificate_id)):
            config = cls.CONFIG['openbadges']
            return config['api_host'] +\
                '/enterprise/certificate/issactivate/' +\
                certificate_id + '/' + user_email

    @classmethod
    def get_token_from_memcache(cls):
        """ Aux function to get the acces token from Memcache """
        token = MemcacheManager.get(cls._MEMCACHE_KEY)
        if not token:
            token = cls.refresh_access_token()
        return token

    @classmethod
    def refresh_access_token(cls):
        """ Retrieve the token again and it save in Memcache """
        token = cls.get_access_token()
        MemcacheManager.set(cls._MEMCACHE_KEY, token)
        return token

    @classmethod
    def send_badge(cls, sent_badge, accest_token):
        """ Send a badge with access_token especified """
        config = cls.CONFIG['openbadges']
        url = config['api_host'] + '/api/issue_badge'
        token = {
            'Authorization': accest_token
        }
        data = {
            'badge': sent_badge.badge_id,
            'email': sent_badge.user_email,
            'name': sent_badge.user_name,
            'template_fields': {}
        }
        res = UrlfetchHelper.post(
            url=url, data=data, url_encode=True, headers=token)
        if res.status_code == 200 or res.status_code == 409:
            response_content = re.sub(r"<!--.*-->", "", res.content)
            cls._process_response(
                res.status_code,
                json.loads(response_content),
                sent_badge)
        elif res.status_code == 401:
            cls.refresh_access_token()
            raise Exception("Reloading access token")
        else:
            exception_str = (str(res.status_code) +
                             ": Can't send badge cause: " +
                             res.content + " \n" +
                             url + " : (" + str(data) + ")")
            raise Exception(exception_str)

    @classmethod
    def get_access_token(cls):
        """ Calls a uri in OpenBadges API to get an accest_token """
        config = cls.CONFIG['openbadges']
        url = config['api_host'] + '/oauth/access_token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': config['client_id'],
            'client_secret': config['client_secret']
        }
        res = UrlfetchHelper.post(
            url=url,
            data=data,
            url_encode=True)

        if res.status_code == 200:
            token = json.loads(res.content)
            acces_token_str = token['access_token']
            return acces_token_str
        else:
            import logging
            logging.error(
                str(res.status_code) +
                ": Can't get acces token cause: " +
                res.content)

    @classmethod
    def _process_response(cls, status_code, response, sent_badge):
        """ Updates SentBadge status depends of response """
        if status_code == 200:
            sent_badge.status = Badges.SENT
        elif status_code == 409:
            sent_badge.status = Badges.ALREADY_SENT
        else:
            import logging
            logging.error(response)
        SentBadgeDAO.set(sent_badge)


def deferred_send_badges(configurations):
    """ Iterate over namespaces and issue badges with status PENDING """
    old_namespace = namespace_manager.get_namespace()
    for configuration in configurations:
        namespace_manager.set_namespace(configuration['_namespace'])

        badges_pending = Badges.get_pending()
        for badge in badges_pending:
            deferred.defer(deferred_send_badge, badge)

    namespace_manager.set_namespace(old_namespace)


def deferred_send_badge(sent_badge):
    """ Issue a badge from a SentBadgeDTO """
    OpenBadges.get_token_and_send_badge(sent_badge)
