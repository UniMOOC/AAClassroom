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
import yaml


class ConfigService(object):
    _config = None
    _config_file = ''

    @classmethod
    def init(cls, conf_file):
        cls._config_file = conf_file

    @classmethod
    def config(cls, key=None):
        if cls._config is None:
            cls._config = yaml.load(open(cls._config_file))

        if key:
            return cls._config[key]
        else:
            return cls._config
