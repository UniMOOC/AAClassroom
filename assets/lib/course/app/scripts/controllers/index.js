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

'use strict';


angular.module('GCB-CMS').controller('IndexCtrl', ['$scope', '$location', '$q', 'Constants', 'UserSvc', 'Resources', 'Processor', 'UIHandler',
  function ($scope, $location, $q, Constants, UserSvc, Resources, Processor, UIHandler) {

    $scope.config = {
        debugMode: Constants.debugMode,
        path: Constants.path,
        userLogued: null
    };

    $scope.googlePlusUser = null;

    $scope.course = null;
    $scope.courseUnprocessed = null;
    Resources.promises.canGoMain = $q.defer();

    //******* RESOURCE QUERIES
    UserSvc.WhenLoad().then(function(){ // Si esta logueado
        $scope.LoadProgress();
    }, function(){
        // Si no esta logueado
    });


    $scope.LoadProgress = function() {
        if(Constants.fakeApi){
            Resources.promises.coursePromise = Resources.Fake.get({file: 'course.json'}).$promise;
            Resources.promises.progressPromise = Resources.Fake.get({file: 'progress.json'}).$promise;
        }
        else{
            Resources.promises.coursePromise = Resources.Course.get().$promise;
            Resources.promises.progressPromise = Resources.Progress.get().$promise;
        }

        Resources.promises.coursePromise.then(function(course){
            Resources.promises.progressPromise.then(function(progress){
                $scope.courseUnprocessed = course;
                var aux = angular.copy($scope.courseUnprocessed);
                Processor.ProcessCourse(aux, progress);
                $scope.course = aux;

                Resources.vars.firstLoad = true;
                Resources.promises.canGoMain.resolve();
            });
        });
    };

    // Cuando el usuario pulsa el botón de loguearse
    $scope.Login = function () {
        UserSvc.Login().then(function(){
            $scope.googlePlusUser = UserSvc.user;
            $scope.googlePlusUser.name = UserSvc.user_full_name;
            $scope.config.userLogued = true;
            $scope.LoadProgress();
        });
    };

    // Cuando se carga el script de GAPI
    $scope.LoadGooglePlus = function(){
        UserSvc.LoadGooglePlus().then(function(){
            $scope.googlePlusUser = UserSvc.user;
            $scope.googlePlusUser.name = UserSvc.user_full_name;
            $scope.config.userLogued = true;
        }, function(){
            $scope.config.userLogued = false;
        });
    };

    $scope.Logout = function(){
        UserSvc.Logout().then(function(){
            UserSvc.CleanVars();
            $scope.googlePlusUser = null;
            $scope.config.userLogued = false;
            $location.path('/');
        });
    };

    $scope.showPrivacy = function(){
        UIHandler.DialogConfirm(
            'Cláusula de Privacidad', '', 'info',
            {icon: 'icon-files-empty', template_name: 'modalPrivacy.html', size: 'lg'}
        );
    };

    $scope.showTermsAndConditions = function(){
        UIHandler.DialogConfirm(
            'Términos y Condiciones del curso básico y especializado de Actívate', '', 'info',
            {icon: 'icon-files-empty', template_name: 'modalTermsAndConditions.html', size: 'lg'}
        );
    };

    $scope.userIsAdmin = function(){
        return UserSvc.user_is_admin;
    }

}]);
