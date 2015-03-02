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


//****** Acordeon

mainModule.directive('myAccordionGroup', function() {
  return {
    require:'^accordion',
    restrict:'EA',
    transclude:true,
    replace: true,
    templateUrl:'views/parts/accordion-unit.html',
    scope: {
      heading: '@',
      index: '@',
      unit: '=',
      isOpen: '=?',
      isDisabled: '=?'
    },
    controller: function() {
      this.setHeading = function(element) {
        this.heading = element;
      };
    },
    link: function(scope, element, attrs, accordionCtrl) {
      accordionCtrl.addGroup(scope);

      scope.$watch('isOpen', function(value) {
        if ( value ) {
          accordionCtrl.closeOthers(scope);
        }
      });

      scope.toggleOpen = function() {
        if ( !scope.isDisabled ) {
          scope.isOpen = !scope.isOpen;
        }
      };
    }
  };
});

mainModule.directive('myAccordionTransclude', function() {
  return {
    require: '^myAccordionGroup',
    link: function(scope, element, attr, controller) {
      scope.$watch(function() { return controller[attr.accordionTransclude]; }, function(heading) {
        if ( heading ) {
          element.html('');
          element.append(heading);
        }
      });
    }
  };
});




mainModule.directive('contenteditable', ['$sce', function($sce) {
    return {
      restrict: 'A', // only activate on element attribute
      require: '?ngModel', // get a hold of NgModelController
      link: function(scope, element, attrs, ngModel) {
        if (!ngModel) return; // do nothing if no ng-model

        // Specify how UI should be updated
        ngModel.$render = function() {
          //element.html($sce.getTrustedHtml(ngModel.$viewValue)); // NO SE DEBE HACER ESTO, PIERDE EL FORMATO
            element.html(ngModel.$viewValue);
        };

        // Listen for change events to enable binding
        element.on('blur', function() {
          scope.$apply(read);
        });

        //read(); // NO SE DEBE INICIALIZAR

        // Write data to the model
        function read() {
          var html = element.html();
          // When we clear the content editable the browser leaves a <br> behind
          // If strip-br attribute is provided then we strip this out
          if ( attrs.stripBr && html == '<br>' ) {
            html = '';
          }
          ngModel.$setViewValue(html);
        }
      }
    };
  }]);

// Cuando finaliza un ng-repeat, se lanza un evento "ngRepeatFinished"
mainModule.directive('onFinishRender', ['$timeout', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }
    };
}]);


mainModule.directive('myNgEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {

            if(event.which === 13) {

                scope.$apply(function (){
                    scope.$eval(attrs.myNgEnter);
                });

                event.preventDefault();
            }
        });
    };
});



// Directiva que observa y actualiza el estado de una colección del scope
//   - Variable a actualizar: watchCollectionChanges="var" , ó la del ng-repeat si no se indica nada
//   - Se debe tener un pageState.dataLoaded y un pageState.dataRendered en el parent scope
mainModule.directive('watchCollectionChanges', ['States', function (States) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            var scopeStr = '';
            var fromCode = false; // Se utiliza para evitar que se rellame al watch cuando se cambia algo dentro de el

            // Si el atributo de la directiva está vacio, lo cogemos del ng-repeat automáticamente
            if(attr.watchCollectionChanges === '' || attr.watchCollectionChanges === undefined)
                scopeStr = attr.ngRepeat.trim().split(/\s+/)[0]; // primera palabra del ng-repeat
            else
                scopeStr = attr.watchCollectionChanges;

            scope.$watchCollection(scopeStr, function (newObject, oldObject) {
                if(!fromCode)
                {
                    if(scope.pageState.dataLoaded && scope.pageState.dataRendered){
                        if(newObject.state == States.UNCHANGED){ // Esta sin modificar
                            newObject.state = States.TO_UPDATE; // Marcarlo para actualizar
                            scope.$emit('dataChanged');
                            fromCode = true;
                        }
                        else if(newObject.state == States.NEW){
                            newObject.state = States.UNCHANGED;
                            fromCode = true;
                        }
                    }
                    else{
                        newObject.state = States.UNCHANGED; // Cuando lo carga, lo inicializamos a loaded
                    }
                }
                else
                    fromCode = false;

            });
        }
    };
}]);
