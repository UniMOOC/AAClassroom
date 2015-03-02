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

angular.module('GCB-CMS')
.controller('ResourcesCtrl',['$scope','$modal', '$q', 'Resources','Constants', 'UserSvc', 'Processor',
function ($scope, $modal, $q, Resources, Constants, UserSvc, Processor) {
    //******* RESOURCE QUERIES
    UserSvc.WhenLoad().then(function(){ // Si esta logueado

        // Cuando le hayamos dado paso
        Resources.promises.canGoMain.promise.then(function(){
            if(Resources.vars.firstLoad === false){
                if(Constants.fakeApi) {
                    Resources.promises.progressPromise = Resources.Fake.get({file: 'progress.json'}).$promise;
                } else {
                    Resources.promises.progressPromise = Resources.Progress.get().$promise;
                }

                // Cuando se hayan completado ambas peticiones
                Resources.promises.progressPromise.then(function(progress){
                    var aux = angular.copy($scope.$parent.courseUnprocessed);
                    Processor.ProcessCourse(aux, progress);
                    $scope.$parent.course = aux;
                    $scope.course = aux;
                });
            }
            else {
                // Si es la primera llamada, ya se ha cargado en el index (skip)
                Resources.vars.firstLoad = false;
            }
        });
    }, function(){
        // Si no esta logueado
    });

    $scope.isModuleOpen = function(module) {
        if (UserSvc.user_is_admin) {
            return true;
        }

        if ($scope.$parent.course.has_started) {
            if ($scope.$parent.course.open_docs) {
                return true;
            }

            return (new Date()) >= module.docs_start_date;
        }
    };

    $scope.isModuleFinished = function(module) {
        if (UserSvc.user_is_admin) {
            return true;
        }

        if ($scope.$parent.course.has_started) {
            if ($scope.$parent.course.open_docs) {
                return true;
            }

            for (var i = 0; i < module.assessmentsList.length; i++) {
                var asm = module.assessmentsList[i];
                if (asm.score === null) {
                    return false;
                }
            }
            return true;
        }
    };
}]);
