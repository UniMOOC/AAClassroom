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
.controller('MainCtrl',['$scope', '$modal', '$location', '$translate', 'courses','Course', 'States',
function ($scope, $modal, $location, $translate, courses, Course, States) {

    // El estado de la página contiene variables generales
    $scope.pageState = {
        dataLoaded: false,
        dataRendered: false,
        btnSaveDisabled: true
    };

    // Insertamos el Modelo de cursos, que se puede usar con un promise (o no)
    courses.$promise.then(function(data){
        $scope.courses = data;
        $scope.pageState.dataLoaded = true;
    });



    //************** MESSAGES

    $scope.$on('ngRepeatFinished', function(){
        $scope.pageState.dataRendered = true;
    });

    $scope.$on('dataChanged', function(){
        $scope.pageState.btnSaveDisabled = false;
    });



    //************** FUNCIONES

    $scope.AddCourse = function(){
        $scope.courses.push(Course.GetNewCourse());

        $('html,body').animate({ // Situamos al usuario sobre la última caja añadida
          scrollTop: $('.box').last().offset().top
        }, 600);

        $scope.$emit('dataChanged'); // Informamos sobre cambios en los datos
    };

    $scope.ChangeImage = function(i){

        // Abrimos el modal para insertar la url
        var modalInstance = $modal.open({
          templateUrl: 'views/parts/modalUrlImg.html',
          controller: 'ModalUrlCtrl',
          resolve: {
            url: function () {
              return $scope.courses[i].imageUrl;
            }
          }
        });

        modalInstance.result.then(function (url) {
            $scope.courses[i].imageUrl = url;
        });
    };

    $scope.CheckIfExistsChanges = function(){
        var state = false;
        angular.forEach($scope.courses, function(course){
            if(course.state !== States.UNCHANGED)
                state = true;
        });
        return state;
    };

    $scope.EditCourse = function(courseId){

        if($scope.CheckIfExistsChanges()){ // Se comprueban si existen cambios

            // Abrimos el modal para insertar la url
            var modalInstance = $modal.open({
              templateUrl: 'views/parts/modalYesNoCancel.html',
              controller: 'ModalYesNoCancelCtrl',
              resolve: {
                headText: function () {
                  return $translate.instant('THERE-ARE-CHANGES');
                }
              }
            });

            modalInstance.result.then(function (result) {
                if(result === 1)
                    $scope.SaveChanges(); // Si hay, se guardan


                $location.path('/course/' + courseId);
            });
        }
        else
            $location.path('/course/' + courseId);
    };

    $scope.SaveChanges = function(){
        angular.forEach($scope.courses, function(course){
            if(course.state === States.UNCHANGED)
                console.log('Curso ' + course.id + ' es Unchanged, NO se guardará');
            else if(course.state === States.TO_UPDATE)
                console.log('Curso ' + course.id + ' modificado, guardando...');
        });
    };

}]);


