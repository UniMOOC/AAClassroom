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

/*global $:false*/
'use strict';

/**
 * @ngdoc function
 * @name gcbCreatorApp.controller:MainCtrl
 * @description
 * # Controlador de la página de inicio, donde se listan los cursos
 */

/*angular.module('GCB-CMS').controller('CourseWatchCtrl', ['$scope', 'States', function ($scope, States) {
    $scope.$watchCollection('course', function (newObject, oldObject) {
        if($scope.pageState.dataLoaded && $scope.pageState.dataRendered){
            if(newObject.state == States.LOADED) // Es nuevo
                newObject.state = States.TO_UPDATE; // Marcarlo para actualizar
        }
    });
}]);*/


angular.module('GCB-CMS')
.controller('MainCtrl',['$scope','$modal', '$q', 'Resources','Constants', 'UserSvc', 'Processor', 'UIHandler',
  function ($scope, $modal, $q, Resources, Constants, UserSvc, Processor, UIHandler) {


    //******* RESOURCE QUERIES
    UserSvc.WhenLoad().then(function(){ // Si esta logueado

        // Cuando le hayamos dado paso
        Resources.promises.canGoMain.promise.then(function(){
            if(Resources.vars.firstLoad === false){
                if(Constants.fakeApi)
                    Resources.promises.progressPromise = Resources.Fake.get({file: 'progress.json'}).$promise;
                else
                    Resources.promises.progressPromise = Resources.Progress.get().$promise;

                // Cuando se hayan completado ambas peticiones
                Resources.promises.progressPromise.then(function(progress){
                        var aux = angular.copy($scope.$parent.courseUnprocessed);
                        Processor.ProcessCourse(aux, progress);
                        $scope.$parent.course = aux;
                        $scope.course = aux;
                });
            }
            else // Si es la primera llamada, ya se ha cargado en el index (skip)
                Resources.vars.firstLoad = false;
        });



    }, function(){
        // Si no esta logueado
    });


    //****** FUNCTIONS

    $scope.CheckDate = function(start, end){
        var currentDate = new Date();
        return (start <= currentDate) && (currentDate <= end);
    };

    $scope.OpenLinks = function(assessment){

        var msg = '';

        angular.forEach(assessment.docs, function(doc){
            msg += '<p><a href="' + doc[1] + '" target="_blank">' + doc[0] + '</a></p>'
        });

        UIHandler.DialogConfirm('Documentos', msg, 'info', {icon: 'icon-files-empty'});
    };


}]);



