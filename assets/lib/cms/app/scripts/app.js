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

var apiPath = '/fake-API/';



var mainModule = angular.module('GCB-CMS', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.sortable',
    'ui.bootstrap',
    'LocalStorageModule',
    'pascalprecht.translate',
    'angular-bootstrap-select',
    'monospaced.elastic',
    'angular-loading-bar'
]);

// Configuramos namespace del localstorage
mainModule.config(function(localStorageServiceProvider){
    localStorageServiceProvider.setPrefix('gcbls');
});


//****************************************
// QUITAR FAKE DELAY

mainModule.config(function($httpProvider){
    $httpProvider.interceptors.push(function($q, $timeout) {
        return {
            'response': function(response) {
                var defer = $q.defer();
                $timeout(function() {
                            defer.resolve(response);
                    }, 1000);
                return defer.promise;
            }
        };
    });
});

//****** Translate
mainModule.config(function($translateProvider){

    var aux = $translateProvider.useStaticFilesLoader({
      prefix: 'i18n/',
      suffix: '.json'
    });

    $translateProvider.preferredLanguage('en');
    $translateProvider.fallbackLanguage('en');
    $translateProvider.useLocalStorage();
});




//************ Rutas

mainModule.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        resolve: {
            'courses': function(Course){
                return Course.query({ file: 'courses.json' });
            }
        }
    })
    .when('/course', {
      templateUrl: 'views/course.html',
      controller: 'CourseCtrl'
    })
    .when('/course/:id', {
      templateUrl: 'views/course.html',
      controller: 'CourseCtrl'
    })
    .otherwise({
        redirectTo: '/'
    });
}]);



// Modificación de directiva de Acordeón


mainModule.config(['$provide', function ($provide){

    $provide.decorator('accordionDirective', function($delegate) {
      var directive = $delegate[0];
      directive.replace = true;
      return $delegate;
    });

    $provide.decorator('accordionHeadingDirective', function($delegate) {
      var directive = $delegate[0];
      directive.require = '^myAccordionGroup';
      return $delegate;
    });

    $provide.decorator('accordionTranscludeDirective', function($delegate) {
      var directive = $delegate[0];
      directive.require = '^myAccordionGroup';
      return $delegate;
    });
}]);




mainModule.filter('num', function() {
    return function(input) {
      return parseInt(input, 10);
    }
});



//********* RUN's

// Añadimos la constante States al $rootScope para poder llamarlo en las vistas .html
mainModule.run(['$rootScope', 'States', function ($rootScope, States) {
    $rootScope.States = States;
}]);
