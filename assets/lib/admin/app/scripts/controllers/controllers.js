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

angular.module('adminModule')
    .controller('asmDateController', ['$scope', '$http','$resource', '$modal', function($scope, $http, $resource, $modal) {
      $scope.eventSources = [];
      $scope.events = [];
      $scope.load = false;
      $scope.new_asm_date = new AsmData({
        'edition'          : 'md-esp-madrid-02',
        'assessment'       : '1',
        'start_date'       : '2015-01-13 10:39:43.0',
        'end_date'         : '2015-01-20 10:39:43.0',
        'attempts'         : 3,
        'check_attendance' : true
      });

      $scope.new_asm_edition = new AsmEdition({
        'code'       : 'md-esp-madrid-02',
        'start_date' : '2015-01-13T10:39:43'
      })

      $scope.activeEdition = 'calendar';
      $scope.createEdition = 'false';
      $scope.createAsmDate = 'false';

      $scope.setActiveEdition = function(view) {
        if ($scope.selected_edition != '') {
          $scope.select_edition();
        }
        $scope.activeEdition = view;
      }
      $scope.showEdition = function(view) {
        return $scope.activeEdition == view;
      }

      $scope.course_info = $resource('api/course/info', {}, {});
      $scope.asm_names = $scope.course_info.get();

      function AsmData(data){
         var self = this;
         angular.extend(self, data);
      }

      function AsmDataClean(data){
         var self = this;
         self.id = data.id;
         self.end_date = data.end;
         self.start_date = data.start;
         self.check_attendance = data.check_attendance;
         self.attempts = data.attempts;
         self.assessment = data.assessment;
      }

      function AsmEdition(data){
         var self = this;
         angular.extend(self, data);
      }

      angular.extend(AsmData, $resource(
        'api/assessment/dates',
        {},
        {
          'all': {
            isArray:false
          },
          'in_edition':{
            url: 'api/assessment/dates?edition=:edition',
            params: {edition:'@edition'}
          },
          'add': {
            method: 'POST',
            headers: {
              'Content-Type':'application/json'
            }
          },
          'update': {
            method: 'POST',
            headers: {
              'Content-Type':'application/json'
            },
            url: 'api/assessment/dates?id=:id',
            params: {id:'@id'}

          },
          'bulk': {
            url: 'api/assessment/dates/_bulk',
            isArray:true,
            method: 'POST'
          }
        }));


     function response_ok(){
        $('#message_response_save').html('<div class="alert alert-success">Guardado correctamente</div>');
      }
      function response_fail(){
        $('#message_response_save').html('<div class="alert alert-danger">Error guardando</div>');
      }

      $scope.selected_edition = '';

      var Edition = $resource('api/editions', {}, {'all':{isArray:false}});
      Edition.all().$promise.then(function(data){
        $scope.editions = data.data;
      });

      $scope.ok = function(){
          console.log("ok");
      }

      $scope.add_new_asm_date = function(){
        var new_one = AsmData.add($scope.new_asm_date);
        $scope.asm_dates.push(new_one);
      }

      $scope.add_new_asm_edition = function() {
       $http.post('api/editions', {'code': $scope.new_asm_edition.code,
                                   'start_date': $scope.new_asm_edition.start_date}, 'application/json').
       success(response_ok).
       error(response_fail);
      }

      var date = new Date();
      var d = date.getDate();
      var m = date.getMonth();
      var y = date.getFullYear();

      $scope.changeTo = 'Español';

      $scope.select_edition = function() {
        if ($scope.selected_edition) {
          var asm_data = {};
          var new_events = [];
          $scope.new_asm_date.edition = $scope.selected_edition;
          AsmData.in_edition({'edition':$scope.selected_edition}).$promise.then(function(data){
            $scope.asm_dates = data.data;
            angular.forEach($scope.asm_dates, function (asm_date) {
              asm_data = {
                id          : asm_date.id,
                title       : asm_date.assessment + ' ' + $scope.asm_names[asm_date.assessment],
                start       : new Date(asm_date.start_date),
                end         : new Date(asm_date.end_date),
                attempts    : asm_date.attempts,
                assessment    : asm_date.assessment,
                check_attendance    : asm_date.check_attendance
              };
              new_events.push(asm_data);

            });
              $scope.events = new_events.slice(0);
              $scope.eventSources.push(new_events);
              $scope.eventSources.splice(0,1);
          });
        }
      }

      $scope.eventsF = function (start, end, timezone, callback) {
        var s = new Date(start).getTime() / 1000;
        var e = new Date(end).getTime() / 1000;
        var m = new Date(start).getMonth();
        var events = [{title: 'Feed Me ' + m,start: s + (50000),end: s + (100000),allDay: false, className: ['customFeed']}];
        callback(events);
      };

      $scope.setAsmData = function(asmData) {
        if (asmData.end == null) asmData.end = asmData.start; //same day, same date
        $scope.asmData = {
          title            : asmData.title,
          id               : asmData.id,
          start            : asmData.start,
          startDay         : asmData.start.getDate(),
          startYear        : asmData.start.getFullYear(),
          startMonth       : asmData.start.getMonth() + 1,
          startTime        : asmData.start.getHours() + ':' + asmData.start.getMinutes(),
          end              : asmData.end,
          endDay           : asmData.end.getDate(),
          endYear          : asmData.end.getFullYear(),
          endMonth         : asmData.end.getMonth() + 1,
          endTime          : asmData.end.getHours() + ':' + asmData.start.getMinutes(),
          attempts         : asmData.attempts,
          check_attendance : asmData.check_attendance
        }
      }

      $scope.alertOnEventClick = function(data, jsEvent, view) {
            $scope.setAsmData(new AsmData(data));
      };

      $scope.updateDate = function(asm, date) {
          date.start.setDate(date.startDay);
          date.start.setMonth(date.startMonth -1);
          date.start.setFullYear(date.startYear);
          date.start.setHours(date.startTime.split(':')[0]);
          date.start.setMinutes(date.startTime.split(':')[1]);

          date.end.setDate(date.endDay);
          date.end.setMonth(date.endMonth -1);
          date.end.setFullYear(date.endYear);
          date.end.setHours(date.endTime.split(':')[0]);
          date.end.setMinutes(date.endTime.split(':')[1]);

          asm.start_date = date.start.toISOString();
          asm.end_date   = date.end.toISOString();
      };

      $scope.updateAssessment = function(asmData) {
        $modal.open({
          template:'<div class="modal-content"><div class="modal-header ng-scope"><h3 class="modal-title">¿Estás seguro?</h3></div><div class="modal-body">Esta operación hará que se cambién los intentos actuales de todos los usuarios, es decir, a cada usuario se la añadirán o quitarán los intentos que se hayan aumentado o disminuido (si no cambian los intentos, no hará nada con los usuarios).<br><strong>La operación puede tardar varios segundos</strong>.</div><div class="modal-footer ng-scope"><button class="btn btn-primary" ng-click="$close()">OK</button><button class="btn btn-warning" ng-click="$dismiss()">Cancel</button></div></div>'
        }).result.then(function(){
          $scope.events.forEach(function (asm) {
            if (asm.id == asmData.id) {
              var new_data = new AsmData(asmData);
              $scope.updateDate(new_data, asmData)
              new_data.attempts = asmData.attempts;
              AsmData.update({'id':new_data.id}, new_data, response_ok, response_fail);
            }
          });
        });
      };

      $scope.updateAllAssessments = function() {
        $modal.open({
          template:'<div class="modal-content"><div class="modal-header ng-scope"><h3 class="modal-title">¿Estás seguro?</h3></div><div class="modal-body">Esta operación hará que se cambiéntodas las fechas modificadas. ¿Quieres continuar?<br><strong>La operación puede tardar varios segundos</strong>.</div><div class="modal-footer ng-scope"><button class="btn btn-primary" ng-click="$close()">OK</button><button class="btn btn-warning" ng-click="$dismiss()">Cancel</button></div></div>'
        }).result.then(function(){
          var new_events = [];
          $scope.events.forEach(function (asm) {
            var new_data = new AsmDataClean(asm);
            new_events.push(new_data)
          });
          AsmData.bulk(new_events, response_ok, response_fail);
        });
      }
      $scope.alertOnDrop = function(data, delta, revertFunc, jsEvent, ui, view) {
        $scope.setAsmData(new AsmData(data));
      };

      $scope.alertOnResize = function(data, delta, revertFunc, jsEvent, ui, view ){
        $scope.setAsmData(new AsmData(data));
      };


      $scope.addRemoveEventSource = function(sources,source) {
        var canAdd = 0;
        angular.forEach(sources,function(value, key){
          if(sources[key] === source){
            sources.splice(key,1);
            canAdd = 1;
          }
        });
        if(canAdd === 0){
          sources.push(source);
        }
      };

      $scope.remove = function(index) {
        $scope.events.splice(index,1);
      };

      $scope.changeView = function(view,calendar) {
        uiCalendarConfig.calendars[calendar].fullCalendar('changeView',view);
      };

      $scope.eventRender = function( event, element, view ) {
        element.attr({'tooltip': event.title,
        'tooltip-append-to-body': true});
      };


      $scope.uiConfig = {
        calendar:{
          height: 450,
          editable: true,
          header:{
            left: 'title',
            center: '',
            right: 'today prev,next'
          },

          lang : 'es',
          firstDay : 1,

          monthNames    :   ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
          dayNames      :   ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
          dayNamesShort :   ["Dom", "Lun", "Mar", "Mier", "Jue", "Vie", "Sab"],

          eventClick    : $scope.alertOnEventClick,
          eventDrop     : $scope.alertOnDrop,
          eventResize   : $scope.alertOnResize,
          eventRender   : $scope.eventRender
        }
      };


      $scope.changeLang = function() {
        if($scope.changeTo === 'Español'){
          $scope.uiConfig.calendar.dayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
          $scope.uiConfig.calendar.dayNamesShort = ["Dom", "Lun", "Mar", "Mier", "Jue", "Vie", "Sab"];
          $scope.changeTo= 'English';
        } else {
          $scope.uiConfig.calendar.dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
          $scope.uiConfig.calendar.dayNamesShort = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
          $scope.changeTo = 'Español';
        }
      };

      $scope.eventSources = [$scope.events];

      $scope.today = function() {
        var dt = new Date();
        $scope.dt = dt.toISOString();
      };

      $scope.today();

  $scope.clear = function () {
    $scope.dt = null;
  };

  // Disable weekend selection
  $scope.disabled = function(date, mode) {
    return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
  };

  $scope.toggleMin = function() {
    $scope.minDate = $scope.minDate ? null : new Date();
  };
  $scope.toggleMin();

  $scope.open = function($event) {
    $event.preventDefault();
    $event.stopPropagation();

    $scope.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yyyy',
    startingDay: 1
  };

  $scope.format = 'yyyy-MM-ddTHH:mm:ss';
 }])
.controller('UserManagerController', ['$scope', '$resource', function($scope, $resource) {

      $scope.course_info = $resource('api/course/info', {}, {});
      $scope.asm_names = $scope.course_info.get();

      function User(data){
         var self = this;
         angular.extend(self, data);
      }

      angular.extend(User, $resource(
        'api/student?email=:email',
        {email:'@email'},
        {
          save:{
            'method':'POST',
            'interceptor': {
              'response': function (data) {$scope.error_message = undefined;},
              'responseError': function(data){$scope.showError(data.status, 'Error guardando los datos');}
            }
          }
        }
      ));

      $scope.search = function(){
        User.get({'email':$scope.email}, function(data){
          $scope.user = data;
          $scope.error_message = undefined;
          $scope.user_attempts = AsmAttempts.get({'email':$scope.email});
        }, function(data){
          $scope.user = undefined;
          if (data.status == 404){
            $scope.showError(data.status, 'Usuario ' + $scope.email + ' no encontrado');
          } else {
        $scope.showError(data.status, 'Error buscando el usuario');
          }

        });
      }

      $scope.showError = function(message_header ,text){
        $scope.error_message_header = message_header;
        $scope.error_message = text;
      }

      function AsmAttempts(data){
         var self = this;
         data.names = new Array();
         angular.forEach(data.attempts_left, function(value, key){
          data.names[key] = AsmData.get({'id':key});
         });

         angular.extend(self, data);

         self.nice_name = function(attemp_id) {
          var asn_name = $scope.asm_names[self.names[attemp_id].assessment];
          return asn_name;
         };
      }

      angular.extend(AsmAttempts, $resource(
        'api/student/attempts?email=:email',
        {email:'@email'},
        {
          get:{
            transformResponse: function(data){
              var jsData = angular.fromJson(data);
              return new AsmAttempts(jsData);
            }
          },
          save:{
            method:'POST',
            transformResponse: function(data){
              var jsData = angular.fromJson(data);
              return new AsmAttempts(jsData);
            }
          }
        }
      ));

      function AsmData(data){
         var self = this;
         angular.extend(self, data);
      }

      angular.extend(AsmData, $resource(
        'api/assessment/dates?id=:id',
        {id:'@id'},
        {}
        ));

      $scope.base_url = $('base').attr('href');

      $scope.AddExtraAttempt = function (asm_name) {
        var asm_id;
        for (var key in $scope.asm_names) {
          if ($scope.asm_names[key] === asm_name) {
            asm_id = key;
            break;
          }
        }

        if (asm_id) {
          ExtraAttempt.save({'email': $scope.email, 'asm_id': asm_id}, function () {
            $scope.search();
          });
        }
      };


      function ExtraAttempt(data){
         var self = this;
         angular.extend(self, data);
      };

      angular.extend(ExtraAttempt, $resource(
        'api/student/extra-attempts',
        {
          email: '@email',
          asm_id: '@asm_id'
        },
        {
          save:{
            'method':'POST',
            'interceptor': {
              'response': function (data) {
                  $scope.error_message = undefined;
               },
              'responseError': function(data){
                $scope.showError(data.status, 'Error otorgando el intento');
              }
            }
          }
        }
      ));
 }]);
