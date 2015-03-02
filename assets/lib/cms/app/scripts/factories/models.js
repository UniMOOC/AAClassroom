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

// CURSO
angular.module('GCB-CMS').factory('Course', ['$resource', 'States', function($resource, States){

    var Course = new function(){
        angular.extend(this, $resource(apiPath + ':file', { file: '@file' } ));

        this.GetNewCourse = function(){
            return {
                "id": -1,
                "title": "",
                "imageUrl": "http://placehold.it/300x170",
                "description": "",
                "active": false,
                "state": States.NEW,
                "countLessons": 0,
                "countSpeakers": 0,
                "countAssessments": 0
            };
        }
    };

    return Course;
}]);


// UNIDAD
angular.module('GCB-CMS').factory('Unit', ['$resource', function($resource){

   var Unit = new function(){
        angular.extend(this, $resource(apiPath + ':file', { file: 'units.json' } ));

        this.GetNewUnit = function(){
            return {
                "id": -1,
                "title": "",
                "badgeUrl": "",
                "active": false,
                "countLessons": 0,
                "countActivities": 0,
                "lessons": [
                ]
            };
        }
    };

    return Unit;
}]);


// LECCIÓN
angular.module('GCB-CMS').factory('Lesson', ['$resource', function($resource){

   return $resource(
        apiPath + ':file', { file: 'lessons.json' }
    );
}]);


// ACTIVIDAD
angular.module('GCB-CMS').factory('Activity', ['$resource', function($resource){

   return $resource(
        apiPath + ':file', { file: 'activities.json' }
    );
}]);


// EXÁMEN
angular.module('GCB-CMS').factory('Assessment', ['$resource', function($resource){

   return $resource(
        apiPath + ':file', { file: 'assessments.json' }
    );
}]);
