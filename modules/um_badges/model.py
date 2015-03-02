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
from google.appengine.ext import db


class SentBadge(db.Model):
    """ Stores a relation between student and badge """
    # Name of the badge
    name = db.StringProperty()

    # ID/Token of the badge
    badge = db.StringProperty()

    # Email of awarded user
    email = db.StringProperty()

    # Issue date
    issued_on = db.DateTimeProperty(auto_now_add=True)

    # Status PENDING, SENT, ALREADY_SENT, ERROR: CODE
    status = db.StringProperty(default='PENDING')


class SentBadgeDTO():
    """ DTO to SentBadge entities """
    def __init__(self, sent_badge=None):
        if sent_badge:
            self.badge_id = sent_badge.badge
            self.user_email = sent_badge.email
            self.user_name = sent_badge.name
            self.issued_on = sent_badge.issued_on
            self.status = sent_badge.status


class SentBadgeDAO():
    """ Generic DAO to filter usual fields for SentBadge """
    @classmethod
    def get(cls, user_email=None, badge_id=None, status=None,
            single_record=False):
        """ Get filtered SEntBadges by any field

            Params:
            - user_email: String
            - badge_id: String
            - status: String (this must be ENDING, SENT, ALREADY_SENT or ERROR)
            - single_record: Boolean if you want just one record

            Returns:
            - None or SentBadgeDTO | [] or [SentBadgeDTO,...]
        """
        badges = cls._get(user_email=user_email, badge_id=badge_id,
                          status=status, single_record=single_record)
        if single_record:
            if badges:
                return SentBadgeDTO(badges)
            else:
                return None
        else:
            if badges:
                return [SentBadgeDTO(sent_badge) for sent_badge in badges]
            else:
                return []

    @classmethod
    def get_before(cls, user_email=None, badge_id=None, status=None,
                   single_record=False, issued_on=None):
        """ Filter query by after issued_on

            The same as get but with issued_on on >= filter posibility
        """

        query = SentBadge.all()
        if user_email:
            query = query.filter('email', user_email)
        if badge_id:
            query = query.filter('badge', badge_id)
        if status:
            query = query.filter('status', status)
        if issued_on:
            query = query.filter('issued_on >=', issued_on)

        badges = None
        if single_record:
            badges = query.get()
        else:
            badges = [badge for badge in query]

        if single_record:
            if badges:
                return SentBadgeDTO(badges)
            else:
                return None
        else:
            return [SentBadgeDTO(sent_badge) for sent_badge in badges]

    @classmethod
    def create(cls, user_email, user_name, badge_id):
        """ Create a SentBadge and return his DTO """
        sent_badge = SentBadge()
        sent_badge.email = user_email
        sent_badge.name = user_name
        sent_badge.badge = badge_id
        sent_badge.put()
        return SentBadgeDTO(sent_badge)

    @classmethod
    def set(cls, sent_badge_dto):
        """ If exist updates a SentBadge """
        sent_badge = cls._get(
            user_email=sent_badge_dto.user_email,
            badge_id=sent_badge_dto.badge_id,
            single_record=True)
        if sent_badge:
            sent_badge.status = sent_badge_dto.status
            sent_badge.put()
        else:
            import logging
            logging.error('Badge not found' + sent_badge_dto.badge_id +
                          ' and ' + sent_badge_dto.user_email)

    @classmethod
    def _get(cls, user_email=None, badge_id=None, status=None,
             single_record=False, ):
        """ Get but retrieving SentBadge instead of SentBadgeDTO """
        query = SentBadge.all()
        if user_email:
            query = query.filter('email', user_email)
        if badge_id:
            query = query.filter('badge', badge_id)
        if status:
            query = query.filter('status', status)
        if single_record:
            return query.get()
        else:
            return [badge for badge in query]
