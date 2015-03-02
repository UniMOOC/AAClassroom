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

""" Handlers to map HTTP verbs to actions """


import json
import datetime

from modules.um_common.utils import is_super_admin
from modules.um_common.utils import TimeHelper
from controllers.utils import BaseHandler

from .services import CourseAPI
from .exceptions import NotFoundException, MethodNotAllowedException,\
    BadRequestException, ForbiddenException


class BaseAPIHandler(BaseHandler):
    """ Handle to create an REST easy API from models.

        Quick guide:
            Create a class inheriting this.
            Set values:
                _MODEL_HANDLER with your db.model
                _DTO_HANDLER with your DTO
                _ID_KEYS with an array string with your model ids name
                _FILTER_KEYS with the keys to filter in list

        This class allows to create an API through db.model configured
        in _MODEL_HANDLER class property. By default it creates:
            - list
            - retrieve
            - create
            - update
            - remove
        You can override this methods to customiza the API actions.
        If you override any method, you can use the methods:
        _request_to_model and _request_to_dto. To use _request_to_dto
        you must to configure property _DTO_HANDLER with your DTO.
        The DTO for this class words like a serialization class,
        thats means that if you don't put this class de object
        returned it will be the model, that is a few ugly to show in JSON.

        Also, you can allow certainly methods in _ALLOWED_METHODS
        property. The posibilities in thes array are:
            ['GET', 'POST', 'PUT', 'DELETE']

        To retrieve you must to config de property _ID_KEYS. If you
        don't config this property the method retrieve and update
        it'll not able.
        To retrieve the model by db.Model key().id() you must to set the
        variable to: ['id'].
        To another ids retrieve you can just complete the array with
        id to filter in the query. For example: ['badge_id']

        The handler handle automactly exceptions produced by request.
        This handle just make self.abort(code) (Read webapp2 docs
        to get more information about it) in exceptions:
            NotFoundException => 404
            BadRequestException => 400
            MethodNotAllowedException => 405

    """

    def handle_exception(self, exception):
        """ Handle exceptions raised from get, post, put or delete.

            This is catched in all methods from API with try and
            catch.
            TODO: Find a way to avoid handle_exception from app parent
            when register the url to handle.
        """
        if isinstance(exception, NotFoundException):
            self.abort(404)
        elif isinstance(exception, BadRequestException):
            self.abort(400, str(exception))
        elif isinstance(exception, MethodNotAllowedException):
            self.abort(405)
        elif isinstance(exception, ForbiddenException):
            self.abort(403)
        else:
            raise exception

    _ALLOWED_METHODS = []
    _MODEL_HANDLER = None
    _DTO_HANDLER = None
    _ID_KEYS = []
    _FILTER_KEYS = []

    def write_json(self, obj):
        """" Write obj to respone.out serialized to JSON """
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(obj, default=self.obj_to_json))

    def obj_to_json(self, obj):
        """ Auxiliar function to serialize automactly to JSON

            That just test if exist a __dict__ property or not and it
            return itself or the object transform to string.
            This is not defined as lambda function because this class
            is too young and is not tested anought to think that this
            function that not will be more complicated.
        """
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, datetime.datetime):
            return TimeHelper.to_GMT1(obj).isoformat()
        else:
            return str(obj)

    def _get_request_json_data(self, key):
        """ Load json_data from request if not exist and return a kay param

            The function test if self has an json_data property. If not
            loads body json and sets json_data to de returned value if exists
            Content-Type: application/json in headers.

            Parameters:
            - key: Key from json object to retrieve

            Return:
            - String with key value or None
        """
        param = None
        if not hasattr(self, 'json_data'):
            self.json_data = {}
            try:
                if self.request.headers.get('Content-Type') and\
                        'application/json' in\
                        self.request.headers['Content-Type'] and\
                        self.request.body:
                    self.json_data = json.loads(self.request.body)
            except ValueError:
                raise BadRequestException('Malformed JSON')
        param = self.json_data.get(key, None)
        return param

    def param(self, key, required=False):
        """ Get a param from request.

            Get the key param from GET or POST variables or from
            JSON body. You can use required parameter to launch or not
            an exception if parameter not exist.

            Parameters:
            - key: Key to retrieve
            - required: Boolean (default False) if key ir required

            Returns:
            - String with key value or None

            Raise:
            - BadRequestException if key doesn't exist and it's required
        """
        param_get = self.request.params.get(key)
        if not param_get:
            param_get = self._get_request_json_data(key)

        if required and not param_get:
            raise BadRequestException(
                'The poroperty ' + key + ' is required')
        return param_get

    def _has_params(self, params):
        """ Test if param is in the request """
        for param in params:
            if not self.param(param):
                return False
        return True

    def retrieve(self):
        """ Handler to retrieve an object by his id """
        model = self._extract_model_by_requested_id()
        if self._DTO_HANDLER:
            model = self._DTO_HANDLER(model)
        self.write_json(model)

    def _extract_model_by_requested_id(self, required=True):
        """ Extract the model requested by id parameters """
        model = None
        if len(self._ID_KEYS) == 1 and self._ID_KEYS[0] == 'id':
            p_value = self.param('id', required)
            model = self._MODEL_HANDLER.get_by_id(long(p_value))
        else:
            query = self._MODEL_HANDLER.all()
            for key in self._ID_KEYS:
                p_value = self.param(key, required)
                query.filter(key, p_value)

            model = query.get()
        if not model:
            raise NotFoundException(
                'Entity ' + p_value + ' does not exist')
        return model

    def list(self):
        """ Handler to list objects """
        objects = None
        query = self._MODEL_HANDLER().all()
        for filter_key in self._FILTER_KEYS:
            filter_value = self.param(filter_key)
            if filter_value:
                query = query.filter(filter_key, filter_value)
        if self._DTO_HANDLER:
            objects = [self._DTO_HANDLER(obj) for obj in query]
        else:
            objects = [obj for obj in query]

        self.write_json({
            'count': len(objects),
            'data': objects
        })

    def create_or_update(self):
        """ Try to get and object requested by id or create a new one """
        try:
            model = self._extract_model_by_requested_id()
            self.update(model)
        except (NotFoundException, BadRequestException):
            self.create()

    def create(self):
        """ Handler to create a new instance from request """
        model = self._request_to_model()
        model.put()
        if self._DTO_HANDLER:
            model = self._DTO_HANDLER(model)
        self.write_json(model)

    def update(self, model):
        """ Handler to update a model requested in id parameters """
        model_updated = self._request_to_model()
        for p_model in self._MODEL_HANDLER._properties:
            attr = getattr(model_updated, p_model, None)
            if attr is not None:
                setattr(model, p_model, attr)
        model.put()
        if self._DTO_HANDLER:
            model = self._DTO_HANDLER(model)
        self.write_json(model)

    def remove(self, model):
        """ Handler to actions to delete model requested to delete """
        model.delete()

    def _request_to_model(self):
        """ Transform the request in a model

            Iterate over self._MODEL_HANDLER _properties and get the values
            from parameters sended in request.
        """
        if self._MODEL_HANDLER:
            model = self._MODEL_HANDLER()
            for p_model, p_type in self._MODEL_HANDLER._properties.items():
                attr = self.param(
                    p_model, (p_type.required and p_model != 'id'))
                attr = self._parse_property(attr, p_type.data_type)
                setattr(model, p_model, attr)
            return model

    def _request_to_dto(self):
        """ Get model from request and transforms to DTO """
        if self._DTO_HANDLER:
            return self._DTO_HANDLER(self._request_to_model())

    def _parse_property(self, data, data_type):
        """ Aux funcion to parse parameters in request """
        if not data:
            return data
        if data_type is datetime.datetime:
            data = TimeHelper.from_isoformat(data)
            return TimeHelper.from_GMT1(data)
        elif data_type is basestring:
            return data
        elif type(data) is dict:
            import json
            return json.dumps(data)
        return data_type(data)

    def _is_allowed_method(self, method):
        """ Return if a method is allowed or raise MethodNotAllowed """
        if (not self._ALLOWED_METHODS or method in self._ALLOWED_METHODS):
            return True
        else:
            raise MethodNotAllowedException(
                'Method ' + method + ' is not allowed')

    @is_super_admin
    def get(self):
        """ Handler to get requests """
        try:
            self._is_allowed_method('GET')
            if len(self._ID_KEYS) > 0 and self._has_params(self._ID_KEYS):
                self.retrieve()
            else:
                self.list()
        except (NotFoundException, ForbiddenException,
                MethodNotAllowedException, BadRequestException,) as e:
            self.handle_exception(e)

    @is_super_admin
    def post(self):
        """ Handler to post requests (same as put) """
        try:
            self._is_allowed_method('POST')
            self.create_or_update()
        except (NotFoundException, ForbiddenException,
                MethodNotAllowedException, BadRequestException,) as e:
            self.handle_exception(e)

    @is_super_admin
    def put(self):
        """ Handler to put requests (same as post) """
        try:
            self._is_allowed_method('PUT')
            self.create_or_update()
        except (NotFoundException, ForbiddenException,
                MethodNotAllowedException, BadRequestException,) as e:
            self.handle_exception(e)

    @is_super_admin
    def delete(self):
        """ Handler to delete requests """
        try:
            self._is_allowed_method('DELETE')
            model = self._extract_model_by_requested_id()
            self.remove(model)
        except (NotFoundException, ForbiddenException,
                MethodNotAllowedException, BadRequestException,) as e:
            self.handle_exception(e)


class CoursesAPIHandler(BaseAPIHandler):
    def get(self, key=None):
        if key is None:
            return self.list()
        else:
            self.write_json(CourseAPI.get_course(key))

    def list(self):
        self.write_json(CourseAPI.get_courses())

    def post(self):
        self.response.out.write("POST API!!!")


class UnitsAPIHandler(BaseAPIHandler):
    def get(self, course_key, unit_key=None):
        if unit_key is None:
            return self.list(course_key)
        else:
            self.write_json(
                CourseAPI.get_unit(course_key, unit_key)
            )

    def list(self, course_key):
        self.write_json(
            CourseAPI.get_units(course_key)
        )

    def post(self):
        self.response.out.write("POST API!!!")
