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


// Simple enumeración
angular.module('GCB-CMS').constant('States', {
       "NEW": -1,
       "UNCHANGED": 0,
       "TO_UPDATE": 1,
   }
);



// Ser
angular.module('GCB-CMS').service('ViewSvc', ['$timeout', function($timeout){


    // Hace Scroll. El parametro withHeight es opcional (true por defecto)
    this.DoScroll = function(selector, index, offset, withHeight){

        if(typeof(withHeight)==='undefined') withHeight = true;

        $timeout(function(){
            var obj = $(selector).eq(index);
            console.log(selector);
            console.log(obj[0]);
            var height = (withHeight ? obj.outerHeight(true) : 0);

            $('html,body').animate({
                scrollTop: obj.offset().top - height - offset
            }, 600);
        }, 50);
    }
}]);
