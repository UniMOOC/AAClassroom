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


angular.module('GCB-CMS').controller('IndexCtrl',['$scope', '$translate', '$timeout', function ($scope, $translate, $timeout) {

    $scope.config = {
        sidebarCollapsed: false,
        debugMode: false
    };

    $scope.InitIndex = function(){

       // Inicializar Menu
       $('#side-menu').metisMenu();

       // Petición para pedir nombre

   };


//************* Traducciones
  //  $translate('ENGLISH').then(function(translation){
//    });


//************* Funciones

    //**** Select Picker
    $scope.MakeInitSelectPicker = function(){
        var lang = $translate.use();
        var word = (lang === 'es' ? $translate.instant('SPANISH') : $translate.instant('ENGLISH'));
        var image = 'images/' + lang + '.png';
        var obj = $('.selectpicker .filter-option.pull-left');

        obj.find('span[translate]').html(word);
        obj.find('img').attr('src',image);
    }

    $scope.UpdateSelectPicker = function(){
        var lang = $('[selectpicker]').selectpicker('val');

        if($translate.use() !== lang)
            $scope.$apply(function() { $translate.use(lang); });

        var word = '';
        if(lang === 'es')
            $translate('SPANISH').then(function (translation) { word = translation; });
        else
            $translate('ENGLISH').then(function (translation) { word = translation; });

        var image = 'images/' + lang + '.png';

        var obj = $('.selectpicker .filter-option.pull-left');
        $timeout(function(){ obj.find('span[translate]').html(word); obj.find('img').attr('src',image); }, 100);
        $timeout(function(){ obj.find('span[translate]').html(word); obj.find('img').attr('src',image); }, 550); // Por si falla el primero
    };

    $scope.InitSelectPicker = function(){
        $timeout(function(){ $scope.MakeInitSelectPicker(); }, 100);
        $timeout(function(){ $scope.MakeInitSelectPicker(); }, 550); // Por si falla el primero
        $timeout(function(){ $scope.MakeInitSelectPicker(); }, 1850);
    };


//************* jQuery

    $(function() {
        $timeout($scope.InitSelectPicker, 40);


        //Loads the correct sidebar on window load, collapses the sidebar on window resize.
        // Sets the min-height of #page-wrapper to window size
        $(window).on('load resize', function() {
            var topOffset = 50;
            var width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
            if (width < 768) {
                $('div.navbar-collapse').addClass('collapse')
                topOffset = 100; // 2-row-menu
            } else {
                $('div.navbar-collapse').removeClass('collapse')
            }

            var height = (this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height;
            height = height - topOffset;
            if (height < 1) height = 1;
            if (height > topOffset) {
                $("#page-wrapper").css("min-height", (height) + "px");
            }
        });


        //******* Bootstrap Select, con esto se arregla el error de la traducción

        $('body').on('click', '.selectpicker a', $scope.UpdateSelectPicker);
    });

}]);
