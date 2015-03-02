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

/**
 * @ngdoc function
 * @name cmsGcbApp.controller:CourseCtrl
 * @description
 * # CourseCtrl
 * Controller of the cmsGcbApp
 */
angular.module('GCB-CMS').controller('CourseCtrl',['$scope', '$routeParams', '$rootScope', '$location', '$timeout', '$modal', 'Course', 'Unit', 'ViewSvc',
 function ($scope, $routeParams, $rootScope, $location, $timeout, $modal, Course, Unit, ViewSvc) {

     // Inicializaciones previas
     $scope.course = Course.GetNewCourse();



    Course.get({ file: 'course-' + $routeParams.id + '.json' }, function(course){
        $scope.course = course;
        $scope.course.unitsList = [];

        Unit.query({ file: 'units.json' }, function(units){
            angular.forEach(units, function(unit){
                unit.opened = false;
            });
            $scope.course.unitsList = units;
        });
    }, function(){ // error, no existe
        $scope.course = null;
    });




     // El estado de la página contiene variables generales
    $scope.pageState = {
        dataLoaded: false,
        dataRendered: false,
        btnSaveDisabled: true,
        path: $location.path()
    };



     // ************ UI SORTABLE ****************** //

    $scope.sortOptions = {
        placeholder: 'sortable-placeholder',
        axis: 'y',
        handle: '.outer-sort',
        start: function(event, ui){ $scope.onSortStart(event, ui); },
        stop: function(event, ui){ $scope.onSortStop(event, ui); }
    };

    $scope.sortOptionsInner = {
        placeholder: 'sortable-placeholder',
        axis: 'y',
        handle: '.inner-sort',
        start: function(event, ui){ $scope.onSortStart(event, ui); },
        stop: function(event, ui){ $scope.onSortStop(event, ui); }
    };

    $scope.onSortStart = function(event, ui){
        ui.helper.css('opacity', 0.6);
        ui.placeholder.height(ui.helper.outerHeight());
    };

    $scope.onSortStop = function(event, ui){
        ui.item.css('opacity', 1);
        // Animacion fadeIn al item que se mueve
        ui.item.siblings().andSelf().eq(ui.item.sortable.dropindex).hide().fadeIn(400);
    };




     //***************** CRUD **********************

     $scope.AddUnit = function(i){
        var obj = Unit.GetNewUnit();
        var index = i;

        if(i < 0){
            $scope.course.unitsList.push(obj);
            index = -1;
        }
        else
            $scope.course.unitsList.splice(i,0,obj);

        var selector = '.box-unit';
        ViewSvc.DoScroll(selector, index, 100);
    };

     $scope.AddLesson = function(i){
         var obj = { "title": "" }
         $scope.course.unitsList[i].lessons.push(obj);

         var index = -1;
         //nth-child empieza a contar desde 1
         var selector = '.box-unit:nth-child('+ (i+1) +') .box-lesson';
         ViewSvc.DoScroll(selector, index, 100);

    };

     $scope.AddActivity = function(unitId, lessonId){
         $scope.course.unitsList[unitId].lessons[lessonId].activity = true;
    };

     $scope.AddAssessment = function(i){

    };

     $scope.ChangeImage = function(i){

        // Abrimos el modal para insertar la url
        var modalInstance = $modal.open({
          templateUrl: 'views/parts/modalUrlImg.html',
          controller: 'ModalUrlCtrl',
          resolve: {
            url: function () {
              return $scope.course.imageUrl;
            }
          }
        });

        modalInstance.result.then(function (url) {
            $scope.course.imageUrl = url;
        });
    };


}]);
