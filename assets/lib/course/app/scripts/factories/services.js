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

angular.module('GCB-CMS').factory('UserSvc', ['$q', '$injector', 'GooglePlus',
  function ($q, $injector, GooglePlus) {

    // Private

    var _defered = $q.defer();

    var _SetVars = function (res, reload) {
        userSvc.idToken = res.id_token;
        userSvc.accessToken = res.access_token;

        var resource = $injector.get('$resource');
        var logout = resource('api/register');

        GooglePlus.loadProfile().then(function (u) { // la peticion ha ido bien
            userSvc.user = u;

            // Enviamos post a api/register y registramos
            logout.save({}, function (res, a, b) {
                userSvc.user_is_admin = res.is_admin;
                userSvc.user_full_name = res.name;

                _defered.resolve();
                if (reload) {
                    $injector.get('$route').reload();
                }
            },function (res) {
                var data = {};

                if (res.status == 403) {
                    if (res.data == 'no_class_attendance') {
                        data.header = 'No has asistido a clase';
                        data.msg = 'No has asistido a clase y por lo tanto no puedes acceder a la aplicación.';
                    } else if (res.data == 'too_many_missed_days') {
                        data.header = 'Has faltado demasiados días';
                        data.msg = 'Has faltado demasiados días a las clases y por lo tanto no puedes acceder a la aplicación.';
                    } else {
                        data.header = 'No estas registrado';
                        data.msg = 'La cuenta <strong>' + userSvc.user.email + '</strong> no está registrada en el curso. Asegurate de que estás usando el correo adecuado.';
                    }
                    userSvc.CleanVars();

                    $injector.get('UIHandler').DialogConfirm(data.header, data.msg, 'error');
                }

                _defered.reject('Api register auth error');
            });
        });
    };


    // Public

    var userSvc = {};

    userSvc.accessToken = '';
    userSvc.idToken = '';
    userSvc.user = '';

    userSvc.CleanVars = function () {
        userSvc.accessToken = '';
        userSvc.idToken = '';
        userSvc.user = '';
    };

    userSvc.refreshToken = function () {
        var promise = GooglePlus.checkAuth();
        promise.then(function (res) {
            userSvc.idToken = res.id_token;
            userSvc.accessToken = res.access_token;
        }, function (err) {
            _defered.reject('Request auth error');
        });
        return promise;
    }

    // Loguea al usuario por primera vez, si tiene la sesión iniciada
    userSvc.LoadGooglePlus = function () {

        if(userSvc.accessToken == '') {
            GooglePlus.checkAuth().then(function (res) {
                _SetVars(res, false); // Seteamos variables
            }, function (err) {
                _defered.reject('Request auth error');
            });
        }
        else
            _defered.reject('Is already loaded');

        return _defered.promise;
    };

    // Loguea al usuario. No se necesitan promises, ya que es User-triggered,
    // por tanto ya se hacargado la libreria
    userSvc.Login = function () {

        _defered = $q.defer(); // hay que resetear _defered, al ser una nueva call

        if(userSvc.accessToken == '') {
            GooglePlus.login().then(function (res) {
                _SetVars(res, true); // Seteamos variables
            }, function (err) {
                _defered.reject('Request auth error');
            });
        }
        else
            _defered.reject('Is already loaded');

        return _defered.promise;
    };

    // Desloguea al usuario
    userSvc.Logout = function () {
        var resource = $injector.get('$resource');
        var revokeUrl = 'https://accounts.google.com/o/oauth2/revoke';
        var logout = resource(revokeUrl + ':tok', {tok: '@token', callback: 'JSON_CALLBACK'},
            { getjsonp: { method: 'JSONP'}});

        // Reiniciamos el defer y hacemos reject, para indicar que se ha deslogueado
        _defered = $q.defer();
        _defered.reject();

        var defer = logout.getjsonp({ token: userSvc.accessToken });
        return defer.$promise;
    };

    // Devuelve la promise, para comprobar si ha finalizado
    userSvc.WhenLoad = function () {
        return _defered.promise;
    };


    return userSvc;
}])



/***************  PROCESSOR  *****************/

angular.module('GCB-CMS').factory('Processor', function () {

  //*** Private

    //** 5o nivel

    var OrderAttempts = function (a, b) {
        if (a.start_date > b.start_date)
            return 1;
        if (a.start_date < b.start_date)
            return -1;
        return 0;
    };

    var CheckCurrentDate = function (startDate, endDate) {
        var current = new Date();

        if(startDate <= current && current <= endDate)
            return true;
        else
            return false;
    };


    //** 4o nivel

    var FindById = function (modules, id) {
        for(var i=0; i < modules.length; i++)
            if(modules[i].unit_id == id)
                return modules[i];

        return false;
    };

    var FindDate = function (asm, unitId, startDate, endDate) {
        for(var i in asm.dates)
            if(asm.unit_id == unitId && asm.dates[i].start_date.getTime() == startDate.getTime() && asm.dates[i].end_date.getTime() == endDate.getTime())
                return asm.dates[i];

        return false;
    };

    var FindCurrentDate = function (asm) {
        for(var i in asm.dates)
            if(CheckCurrentDate(asm.dates[i].start_date, asm.dates[i].end_date))
                return asm.dates[i];

        return false;
    };

    var OnlyLastAttemptLeft = function (asm) {
        for (var i = 0; i < asm.dates.length - 1; i++) {
            if (asm.dates[i].attempts_left > 0) {
                return false;
            }
        }
        return true;
    };

    var SetAttemptsAndDates = function (asm, progress, key) {

//        console.log(asm);
//        console.log(key);
//        console.log(progress);
//
        var arrAttempt = key.split(';'); //0:id, 1:unit_id, 2:startDate, 3:endDate

        var startDate = new Date(arrAttempt[2]);
        var endDate = new Date(arrAttempt[3]);

        // Buscar la date correcta, y añadirle attempts_done
        var date = FindDate(asm, arrAttempt[1], startDate, endDate);

        if(date !== false) {
            date.attempts_left = progress.attempts[key];
            date.start_date = startDate; // Se pasan a objeto desde
            date.end_date = endDate;   // un datetime ISO 8601

            // Seteamos el array de intentos que leerá la vista, para poner iconos
            date.attempts_view = [];
            var num_red_exs = date.attempts - date.attempts_left;
            var num_gray_exs = date.attempts - num_red_exs;

            var aux = asm.score && asm.score >= asm.min_score && date.attempts_left < date.attempts;
            var checkmark = (aux ? 1 : 0)

            // Si esta aprobado, hay que insertar un checkmark, por tanto una x roja menos
            num_red_exs -= checkmark;

            for(var i=0; i < num_red_exs; i++)
                date.attempts_view.push('fail');

            if(checkmark == true)
                date.attempts_view.push('pass');

            for(var i=0; i < num_gray_exs; i++)
                date.attempts_view.push('clean');
        }
    };





    //** 3r nivel

    var InsertIntoParent = function (modules, mod) {
        var parent = FindById(modules, mod.unit_parent);
        if(parent !== false) {
            if(!parent.assessmentsList)
                parent.assessmentsList = [mod];
            else
                parent.assessmentsList.push(mod);
        }
    };

    var InsertProgressIntoAsm = function (modules, progress, id_asm) {
        var asm = FindById(modules, id_asm);

        if(asm !== false && asm.dates) {
            asm.score = progress.score;

            // Procesamos e insertamos datos en el asm
            for (var key in progress.attempts)
                SetAttemptsAndDates(asm, progress, key);

            asm.dates.sort(OrderAttempts);

            // Parseamos docs (vienen como string)
            if(asm.docs && asm.docs != "")
                asm.docs = angular.fromJson(asm.docs);

            asm.available = (FindCurrentDate(asm) ? true : false);

            asm.only_last_attempt_left = OnlyLastAttemptLeft(asm);

            asm.start_date = asm.dates[0].start_date;
            asm.end_date = asm.dates[asm.dates.length - 1].end_date;

            asm.docs_start_date = new Date(asm.start_date);
            asm.docs_start_date.setHours(8)

            asm.open_docs = asm.docs && (new Date()) >= asm.docs_start_date;
        }
    };


    var SetState = function (mod) {

        mod.start_date = mod.assessmentsList.reduce(function (prev, curr) {
            return prev.start_date <= curr.start_date ? prev : curr;
        }).start_date;

        mod.end_date = mod.assessmentsList.reduce(function (prev, curr) {
            return prev.end_date >= curr.end_date ? prev : curr;
        }).end_date;

        // 1 - Comprobamos fechas (cerrado, abierto)
        // 2 - Si tiene todos los asm completados, esta completado
        for (var j in mod.assessmentsList) {

            var asm = mod.assessmentsList[j];

            for (var k in asm.dates) {
                var date = asm.dates[k];

                if(CheckCurrentDate(date.start_date, date.end_date)) {
                    if(date.attempts_left == 0)
                        asm.noAttemptsInCurrentDate = true;
                }
            }
        }

        mod.completed_asms = mod.assessmentsList.reduce(function (prev, curr) {
            return curr.score >= curr.min_score ? prev + 1 : prev;
        }, 0);

        mod.docs_start_date = new Date(mod.start_date);
        mod.docs_start_date.setHours(8);

        if (mod.completed_asms == mod.assessmentsList.length) {
            mod.state = 'done';
        } else {
            var now = new Date();
            mod.state = (mod.start_date <= now && mod.end_date >= now) ? 'open' : 'closed';
        }
    };

    var AddTooltips = function (mod) {

        for (var i in mod.assessmentsList) {
            var date = FindCurrentDate(mod.assessmentsList[i]);

            // Si no hay convocatoria abierta
            if(!date) {
                mod.assessmentsList[i].tooltipAsm = 'No hay ninguna convocatoria abierta actualmente';
            }
            // Si no quedan intentos para la convocatoria abierta actual
            else if(date.attempts_left == 0) {
                mod.assessmentsList[i].tooltipAsm = 'No tienes más intentos en esta convocatoria';
            }
        }
    };

    var CheckFinalAsmCanDo = function (modules) {
        for (var i in modules)
            for (var j in modules[i].assessmentsList)
                if(modules[i].assessmentsList[j].score < modules[i].assessmentsList[j].min_score)
                    return false;

        return true;
    };



    //** 2o nivel

    var SortModulesLevels = function (course) {

        for(var i=0; i < course.units.length; i++) {
            if(course.units[i].type == 'A') {
                course.units[i].min_score = parseInt(course.units[i].min_score) || null;
                InsertIntoParent(course.units, course.units[i]);
                course.units.splice(i, 1);
                i--; //atrasar una posicion, por el splice
            }
            else if(course.units[i].type == 'F') {
                course.units[i].min_score = parseInt(course.units[i].min_score) || null;
                course.finalAsm = course.units[i];
                course.units.splice(i, 1);
                i--;
            }
        }
    };

    var AddProgressToAsm = function (modules, progress) {

        for (var i in modules)
            if(modules[i].dates)
                for (var j in modules[i].dates) {
                    modules[i].dates[j].start_date = new Date(modules[i].dates[j].start_date);
                    modules[i].dates[j].end_date = new Date(modules[i].dates[j].end_date);
                }


        for (var key in progress)
            if (progress.hasOwnProperty(key))
                InsertProgressIntoAsm(modules, progress[key], key);


        for (var i in modules) {
            if (modules[i].required_asms) {
                for (var j = 0; j < modules[i].required_asms.length; j++) {
                    var module = FindById(modules, modules[i].required_asms[j]);
                    if (module.score || module.score < module.min_score) {
                        modules[i].available = false;
                        break;
                    }
                }
            }
        }

    };

    var PostProcess = function (course) {
        for (var i in course.units) {
            SetState(course.units[i]);
            AddTooltips(course.units[i]);

            // Parseamos docs (vienen como string)
            if(course.units[i].docs && course.units[i].docs != "")
                course.units[i].docs = angular.fromJson(course.units[i].docs);
        }
        course.finalAsm.canDo = CheckFinalAsmCanDo(course.units);

        if(!course.finalAsm.canDo)
            course.finalAsm.tooltipAsm = 'Debes completar los demás exámenes para poder hacer el final';

        course.start_date = course.units.reduce(function (prev, curr) {
            return prev.start_date < curr.start_date ? prev : curr;
        }).start_date;
        course.start_date.setHours(8);

        course.has_started = new Date() >= course.start_date;
        course.is_basic = function(){
            return (course.edition_name.indexOf("-bas-") > -1)
        };

        for(var i=0; i < course.units.length; i++) {
            if(course.units[i].type == 'U') {
                course.units[i].can_get_certificate = course.finalAsm.score != null;
            }
        }
    };


    //*** Public

    var processor = {};

    processor.ProcessCourse = function (course, progress) {
        AddProgressToAsm(course.units, progress);
        SortModulesLevels(course);
        PostProcess(course); //Añade estados y otras variables
    };

    return processor;
})




/***************  UI HANDLER  *****************/

.factory('UIHandler', ['$modal', 'Constants', function ($modal, Constants) {


    var GetIcon = function (type) {
        if(type == 'error' || type == 'warning')
            return 'glyphicon glyphicon-warning-sign';
        else if(type == 'success')
            return 'icon-checkmark';
        else if(type == 'info')
            return 'glyphicon glyphicon-info-sign';
    }



    var uiHandler = {};

    // type = [error, warning, success, info]. Determina color y icono

    uiHandler.DialogConfirm = function (header, message, type, options) {
        var options = options || {};
        options.icon = options.icon || GetIcon(type);
        options.redirect = options.redirect || false;
        options.size = options.size || 'md'; // 'sm', 'md' o 'lg'
        options.template_name = options.template_name || 'modalConfirm.html';
        options.backdrop = options.backdrop || 'static';
        return $modal.open({
          templateUrl: Constants.path + '/views/parts/' + options.template_name,
          controller: 'ModalContent',
          size: options.size,
          backdrop: options.backdrop,
          resolve: {
            data: function () {
              return {header: header, msg: message , type: type , options: options};
          }}
        });
    };

    return uiHandler;
}]);




angular.module('GCB-CMS').factory('OpenBadgesSvc',['$resource',
  function ($resource) {
    return $resource(
            'https://gaeopenbadges.appspot.com/api/issuer/issactivate/badge/:badge_id',
            { 'badge_id': '@badge_id'},
            {});

}])
