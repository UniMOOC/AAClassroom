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

angular.module('GCB-CMS')
.controller('AssessmentCtrl',['$scope', '$q', '$routeParams', '$location', 'Resources','Constants','UserSvc', 'UIHandler', 'OpenBadgesSvc',
  function ($scope, $q, $routeParams, $location, Resources, Constants, UserSvc, UIHandler, OpenBadgesSvc) {
    $scope.assessment = null;

    UserSvc.WhenLoad().then(function(){
        Resources.Assessment.get({'unit_id': $routeParams.unit_id}, function(assessment){
            Resources.promises.canGoMain.promise.then(function(){

                assessment.preamble = 'Una vez finalices el examen selecciona “Enviar respuestas”. Si superas el examen (con un 80% de aciertos), no tendrás que volver a realizarlo ya que las respuestas quedarán registradas. Recuerda que hoy solo tienes <strong>';
                if ($scope.course.is_basic()) {
                    assessment.preamble += 'tres intentos';
                } else {
                    assessment.preamble += 'un intento';
                }

                assessment.preamble += '</strong> para aprobar el examen de este módulo.';
                if (! $scope.isLastAsmDate(assessment)) {
                    assessment.preamble += ' En caso de no superar el examen, una vez que acabes todo el ' + $scope.course.title + ', tendrás otra oportunidad para conseguirlo. ¡Mucha suerte!';
                }

                $scope.assessment = assessment;
                $scope.assessmentCopy = assessment;
                if (window.localStorage.getItem($routeParams.unit_id)) {
                    $scope.assessment.questions = JSON.parse(window.localStorage.getItem($routeParams.unit_id));
                } else {
                    $scope.assessment.questions = $scope.Shuffle($scope.assessment.questions);
                }
                var asm         = $scope.FindAsmById($routeParams.unit_id);
                var date        = $scope.FindDate(asm);
                $scope.attempts = date.attempts_left;
            });

        }, function(res){
            var msg = '', header = '';
            if (res.status == 403 && res.data == 'no_dates_available') {
                header = 'Convocatoria cerrada';
                msg = 'Esta convocatoria esta cerrada en el dia de hoy.';
            } else if (res.status == 403 && res.data == 'no_attempts_left') {
                header = 'Intentos agotados';
                msg = 'No te quedan más intentos en esta convocatoria.';
            } else if (res.status == 403 && res.data == 'no_class_attendance') {
                header = 'Clases presenciales';
                msg = 'No puedes hacer el examen porque no has asistido a la clase presencial correspondiente.';
            } else if (res.status == 403 && res.data == 'too_many_missed_days') {
                header = 'Has faltado demasiados días';
                msg = 'Has faltado demasiados días a las clases y por lo tanto no puedes hacer el examen.';
            }

            if (msg !== '') {
                UIHandler.DialogConfirm(header, msg, 'error', {redirect: true, backdrop: 'true'});
            }

            $scope.assessment = null;
        });
    }, function(){
        // Si no esta logueado, redirigimos al inicio
        $location.path('/').replace();
    });

    $scope.FindAsmById = function(id){
        for(var i=0; i < $scope.$parent.course.units.length; i++){
            for(var j=0; j < $scope.$parent.course.units[i].assessmentsList.length; j++){
                if($scope.$parent.course.units[i].assessmentsList[j].unit_id == id){
                    return $scope.$parent.course.units[i].assessmentsList[j];
                }
            }
        }

        if($scope.$parent.course.finalAsm.unit_id == id){
            return $scope.$parent.course.finalAsm;
        }

        return false;
    };

    $scope.FindDate = function(asm){

        var now = new Date();

        for(var i in asm.dates)
            if(asm.dates[i].start_date <= now && asm.dates[i].end_date >= now)
                return asm.dates[i];

        return false;
    };

    $scope.Mark = function(){
        // Montar json con {'01': 2, '02': 2} y POSTear
        var answers = {};

        angular.forEach($scope.assessment.questions, function(obj, index){
          answers[obj.key] = obj.answer;
        });

        var questions_left = false;
        for (var key in answers) {
            if (answers[key] === undefined) {
                questions_left = true;
                break;
            }
        }

        if (questions_left) {
            var msg = 'Te has dejado algunas preguntas sin responder. ¿Deseas enviar el examen o continuar haciéndolo?';
            var modal = UIHandler.DialogConfirm('Preguntas sin responder', msg, 'info', {template_name: 'modalUnansweredQuestions.html', backdrop: 'true'});
            modal.result.then(function() {
                $scope.SendAnswers($routeParams.unit_id, answers);
            }, function() {

            })
        } else {
            $scope.SendAnswers($routeParams.unit_id, answers);
        }


    };

    $scope.SendAnswers = function(unit_id, answers) {
        Resources.Assessment.save({'unit_id': unit_id, 'answers': answers}, function(response){
            $scope.resetQuestions(unit_id);
            var header = null, msg = null, type = null, options = null;
            // var header = 'Aprobado', msg = '', type = 'success', feedback = '';
            if (response.score >= $scope.assessment.min_score){
                var badges_issued = [];
                for (var badge_index in response.badge) {
                    var badge_id = response.badge[badge_index];
                    badges_issued.push(OpenBadgesSvc.get({'badge_id': badge_id}).$promise);
                }

                $q.all(badges_issued).then(function(data){
                    header = 'Aprobado';
                    type   = 'success'
                    msg    = {
                      main : '',
                      available : '',
                      failed: false,
                      feedback: {wrong: [], empty: [], correct: null, questionsNumber : response.feedback.length},
                      wrongWidth: '',
                      emptyWidth: '',
                      correctWidth: '',
                      userEmail: UserSvc.user.email,
                      badges: data
                    }

                    msg.main = '¡Enhorabuena! Has aprobado obteniendo un ' + response.score + '%. ';
                    if (data.length > 1) {
                      msg.main += 'Aquí está tus badge: ';
                      msg.available = '(puede que tarden unos segundos en estar disponibles)';
                    } else {
                      msg.main += 'Aquí está tu badge: ';
                      msg.available = '(puede que tarde unos segundos en estar disponible)';
                    };

                    $scope.seedFeedback(msg, response.feedback);
                    $scope.msg = msg;
                    UIHandler.DialogConfirm(header, msg, type, {redirect: true, template_name: 'modalExamResult.html', backdrop: 'static'});
                });

            } else {
                header = 'Has agotado el intento de hoy.';
                type = 'error';
                msg = {main: '',
                       failed: true,
                       feedback: {wrong: [], empty: [], correct: null, questionsNumber : response.feedback.length},
                       wrongWidth: '',
                       emptyWidth: '',
                       correctWidth: ''
                       };

                $scope.attempts--;

                msg.main = '¡Oh! En esta ocasión no has superado el test, tu puntuación es '
                    + response.score + '% y necesitas un mínimo de ' + Math.floor($scope.assessment.min_score)
                    + '% de aciertos para superarlo.'

                if (! $scope.isLastAsmDate($scope.assessment)) {
                    msg.main += ' Hoy no puedes volver a realizar este test, pero recuerda que cuando finalices el curso Especializado de Marketing Digital, tendrás otra oportunidad para poder superarlo.';
                } else {
                    msg.main += ' Desgraciadamente este era tu último intento.'
                }

                $scope.seedFeedback(msg, response.feedback);
                $scope.msg = msg;
                UIHandler.DialogConfirm(header, msg, type, {redirect: true, template_name: 'modalExamResult.html', backdrop: 'static'});
            }

        }, function(res) {
            if(res.status != 500){
                var msg = 'Se ha producido un error corrigiendo tu examen. Recarga la página (tus respuestas no se perderán) y vuelve a enviar el examen.';
                UIHandler.DialogConfirm('Error', msg, 'error');
            }
        });
    }

    $scope.percentage = function(value, max) {
      return (value * 100) / max;
    }

    $scope.seedFeedback = function(msg, responseFeedback) {
      for (var question in responseFeedback) {
        if (responseFeedback[question].type == 'wrong') {
          msg.feedback.wrong.push(responseFeedback[question]);
        } else if (responseFeedback[question].type == 'not_answered') {
          msg.feedback.empty.push(responseFeedback[question]);
        }
      };

      msg.feedback.correct = responseFeedback.length - msg.feedback.wrong.length - msg.feedback.empty.length;
      msg.correctWidth     = $scope.percentage(msg.feedback.correct, responseFeedback.length);
      msg.emptyWidth       = $scope.percentage(msg.feedback.empty.length, responseFeedback.length);
      msg.wrongWidth       = $scope.percentage(msg.feedback.wrong.length, responseFeedback.length);
    }

    $scope.change = function(question, value) {
        $scope.assessment.questions[question -1]['checked'] = value;
        window.localStorage.setItem($routeParams.unit_id, JSON.stringify($scope.assessment.questions));
      }

    $scope.resetQuestions = function(unit_id) {
      window.localStorage.removeItem(unit_id);
      $scope.assessment = $scope.assessmentCopy;
    }

    $scope.Shuffle = function(array) {
        var currentIndex = array.length, temporaryValue, randomIndex ;

        // While there remain elements to shuffle...
        while (0 !== currentIndex) {

            // Pick a remaining element...
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex -= 1;

            // And swap it with the current element.
            temporaryValue = array[currentIndex];
            array[currentIndex] = array[randomIndex];
            array[randomIndex] = temporaryValue;
        }

        return array;
    };

    $scope.isLastAsmDate = function(assessment) {
        var asm_unit = $scope.FindAsmById(assessment.unit_id);
        return $scope.FindDate(asm_unit) === asm_unit.dates[asm_unit.dates.length - 1];
    }
  }]);
