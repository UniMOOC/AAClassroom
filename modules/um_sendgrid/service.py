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
# encoding=utf8

import json
import logging

import appengine_config

from sendgrid import SendGridClient
from sendgrid import Mail

from google.appengine.api import taskqueue

from modules.um_common.utils import ConfigReader


def check_sending_allowed(func):
    def inner_func(*args, **kwargs):
        if not SendGrid.sending_allowed():
            config = SendGrid.CONFIG['local_send']
            logging.warning(config['message'])
        else:
            return func(*args, **kwargs)
    return inner_func


class SendGrid(object):
    _sd = None
    CONFIG = ConfigReader('modules/um_sendgrid/config.yaml')

    @classmethod
    def _get_sd_client(cls):
        if cls._sd is None:
            user, password = cls._get_user_pass()
            cls._sd = SendGridClient(user, password, secure=True)
        return cls._sd

    @classmethod
    def _get_user_pass(cls):
        sd_confg = cls.CONFIG['credentials']
        return sd_confg['username'], sd_confg['password']

    @classmethod
    def sending_allowed(cls):
        config = cls.CONFIG['local_send']
        return appengine_config.PRODUCTION_MODE or config['enabled']

    @classmethod
    @check_sending_allowed
    def send_email(cls, from_adr, to_adr, subject, body,
                   template_id=None, substitutions=None, categories=None):
        message = Mail()

        message.set_from(from_adr)
        message.add_to('<{}>'.format(to_adr))
        message.set_subject(subject)
        message.set_html(body)

        if template_id:
            message.add_filter('templates', 'template_id', template_id)

        if substitutions:
            for key, value in substitutions:
                message.add_substitution('-{}-'.format(key), value)

        if categories:
            for cat in categories[:10]:
                message.add_category(cat)

        sd = cls._get_sd_client()
        sd.send(message)

    @classmethod
    def async_send_email(cls, from_adr, to_adr, subject, body,
                         template_id=None, subs=None, categories=None):
        params = {
            'from_adr': from_adr,
            'to_adr': to_adr,
            'subject': subject,
            'body': body,
            'template_id': template_id if template_id else '',
            'substitutions': json.dumps(subs) if subs else '',
            'categories': json.dumps(categories) if categories else ''
        }
        config = cls.CONFIG['async']

        taskqueue.add(
            url=config['endpoint'],
            params=params,
            queue_name=config['queue_name']
        )

    @classmethod
    @check_sending_allowed
    def send_welcome(cls, to_adr):
        welcome_config = cls.CONFIG['templates']['welcome']
        cls.async_send_email(
            welcome_config['address'], to_adr,
            welcome_config['subject'], ' ',
            template_id=welcome_config['id'],
            categories=[welcome_config['category']]
        )
