// Copyright 2015 UniMOOC. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


/*global jQuery:false*/
'use strict';

/**
 * @ngdoc overview
 * @name pppApp
 * @description
 * # pppApp
 *
 * Main module of the application.
 */



var mainModule = angular.module('GCB-CMS', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'googleplus',
    'angular-loading-bar',
    'ngUAParser'
]);


//************ ROUTES & CONFIG

mainModule.config(['$routeProvider','Constants', function ($routeProvider, Constants) {
    $routeProvider
    .when('/', {
        templateUrl: Constants.path + '/views/main.html',
        controller: 'MainCtrl'
    })
    .when('/assessment/:unit_id', {
        templateUrl: Constants.path + '/views/assessment.html',
        controller: 'AssessmentCtrl'
    })
    .when('/resources', {
        templateUrl: Constants.path + '/views/resources.html',
        controller: 'ResourcesCtrl'
    })
    .when('/extra-attempts/:url_hash', {
        templateUrl: Constants.path + '/views/extra_attempts.html',
        controller: 'ExtraAttemptsCtrl'
    })
    .otherwise({
        redirectTo: '/'
    });
}]);




mainModule.config(['GooglePlusProvider', function(GooglePlusProvider) {
     GooglePlusProvider.init({
        clientId: '',
        apiKey: '',
        scopes: 'https://www.googleapis.com/auth/plus.me email'
     });
}]);


mainModule.config(['$tooltipProvider', function($tooltipProvider) {
    var parser = new UAParser();
    var result = parser.getResult();
    var touch = result.device && (result.device.type === 'tablet' || result.device.type === 'mobile');
    var options = {};
    if (touch) {
      options = {
        trigger: 'dontTrigger', // default dummy trigger event to show tooltips
        appendToBody: false
      };
    } else {
      options = {
        appendToBody: true
      }
    }
     $tooltipProvider.options(options);
}]);



//************** DECORATORS

mainModule.config(['$provide','Constants', function ($provide, Constants){

    $provide.decorator('accordionGroupDirective', ['$delegate', function($delegate) {
      var directive = $delegate[0];

      directive.templateUrl = Constants.path + "/views/parts/accordionHeading.html";


      /* Por un bug en Angular > 1.3.x, no se puede usar:
           angular.extend(directive.scope, { module:'@' });

         Ver: http://stackoverflow.com/questions/27637660/angularjs-decorator-binding-new-variables-to-directive

         Así que hay que hacerlo de la siguiente manera
      */

      directive.$$isolateBindings['module'] = {
          attrName: 'module',
          mode: '=',
          collection: false,
          optional: true
      };



      return $delegate;
    }]);
}]);

mainModule.config(['$provide', function ($provide){

    $provide.decorator('accordionDirective', ['$delegate', function($delegate) {
      var directive = $delegate[0];
      directive.replace = true;
      return $delegate;
    }]);
}]);



//******************** INTERCEPTORS
// Interceptor, que añade el idToken a las peticiones a la api
mainModule.config(['$httpProvider', function($httpProvider){
    function isRequestToApi(config) {
        return config.url.indexOf('api/') == 0;
    }

    var authInterceptor = ['$q', '$location', '$injector', 'UserSvc',
        function ($q, $location, $injector, UserSvc) {
            return {
                // Para las peticiones, se comprueba que exista un token y que sea una
                // peticion a la api. Si se cumple se añade el token
                request: function (config) {
                    config.headers = config.headers || {};
                    if (UserSvc.idToken != '' && isRequestToApi(config)){
                        config.headers['Id-Token'] = UserSvc.idToken;
                    }

                    return config;
                },
                responseError: function (res){
                    if(res.status == 500){
                        var msg = 'Ha ocurrido un error en el servidor. Inténtalo de nuevo.';
                        $injector.get('UIHandler').DialogConfirm('Error', msg, 'error', {redirect: true});
                    } else if (res.status == 401){
                        if (isRequestToApi(res.config)){
                          UserSvc.refreshToken();
                          var msg = 'Sesión caducada. Se ha refrescado la sesión. Inténtalo de nuevo.';
                          $injector.get('UIHandler').DialogConfirm('Error: Sesión caducada', msg, 'error', {redirect: true});
                        }
                    }
                    return $q.reject(res);
                }
            }
        }
    ];

    $httpProvider.interceptors.push(authInterceptor);
}]);






//******************** DIRECTIVES


// Cuando finaliza un ng-repeat, se lanza un evento "ngRepeatFinished"
mainModule.directive('onFinishRender', ['$timeout', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }
    };
}]);




//******************** FILTERS

mainModule.filter('unsafe',['$sce',  function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
}]);
