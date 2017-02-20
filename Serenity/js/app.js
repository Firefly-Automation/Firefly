
(function () {

    var app = angular.module('SerenityApp', ['ngMaterial', 'ngMessages', 'material.svgAssetsCache']);
        app.config(function($mdThemingProvider) {
            $mdThemingProvider.theme('default');

            //$mdThemingProvider.theme('altTheme')
            //    .backgroundPalette('grey',{'default': '900'})
            //                .dark();
            $mdThemingProvider.theme('default-dark').dark(true);
            $mdThemingProvider.theme('orange').primaryPalette('orange').accentPalette('grey',{'default':'400'});
            $mdThemingProvider.theme('orange-dark').primaryPalette('orange').accentPalette('grey',{'default':'600'}).dark(true);

            $mdThemingProvider.theme('blue').primaryPalette('blue');
            $mdThemingProvider.theme('blue-dark').primaryPalette('blue').dark(true);

            $mdThemingProvider.theme('cyan').primaryPalette('cyan');
            $mdThemingProvider.theme('cyan-dark').primaryPalette('cyan').dark(true);

            $mdThemingProvider.theme('green').primaryPalette('light-green');
            $mdThemingProvider.theme('green-dark').primaryPalette('light-green').dark(true);

            $mdThemingProvider.theme('pink').primaryPalette('pink');
            $mdThemingProvider.theme('pink-dark').primaryPalette('pink').dark(true);

            //$mdThemingProvider.setDefaultTheme('altTheme');
            $mdThemingProvider.alwaysWatchTheme(true);
        });

        app.controller('SerenityCtrl', function ($scope, $timeout, $mdSidenav, $log, $http) {
        $scope.toggleLeft = buildDelayedToggler('left');
        $scope.toggleRight = buildToggler('right');
        $scope.isOpenRight = function(){
          return $mdSidenav('right').isOpen();
        };

        $http.get('/theme', {timeout:5000})
        .then(function(res)
        {
          $scope.theme = res.data;
          console.log($scope.theme)
        });

        $scope.themes = ['default', 'default-dark', 'orange', 'orange-dark', 'blue', 'blue-dark', 'cyan', 'cyan-dark',
        'green', 'green-dark', 'pink', 'pink-dark'];



        /**
         * Supplies a function that will continue to operate until the
         * time is up.
         */
        function debounce(func, wait, context) {
          var timer;

          return function debounced() {
            var context = $scope,
                args = Array.prototype.slice.call(arguments);
            $timeout.cancel(timer);
            timer = $timeout(function() {
              timer = undefined;
              func.apply(context, args);
            }, wait || 10);
          };
        }

        /**
         * Build handler to open/close a SideNav; when animation finishes
         * report completion in console
         */
        function buildDelayedToggler(navID) {
          return debounce(function() {
            $mdSidenav(navID)
              .toggle()
              .then(function () {
                $log.debug("toggle " + navID + " is done");
              });
          }, 200);
        }

        function buildToggler(navID) {
          return function() {
            $mdSidenav(navID)
              .toggle()
              .then(function () {
                $log.debug("toggle " + navID + " is done");
              });
          }
        }
      });

      app.controller('LeftCtrl', function ($scope, $timeout, $mdSidenav, $log) {
        $scope.close = function () {
          $mdSidenav('left').close()
            .then(function () {
              $log.debug("close LEFT is done");
            });

        };
      });

      app.controller('RightCtrl', function ($scope, $timeout, $mdSidenav, $log) {
        $scope.close = function () {
          $mdSidenav('right').close()
            .then(function () {
              $log.debug("close RIGHT is done");
            });
        };
      });

      app.controller('ThemeCtrl', function ($scope, $http) {
        $scope.selectedTheme = 'BLAH';

        $scope.getTheme = function(){
            $scope.selectedTheme = $scope.theme;
            return $scope.theme;
        };

        $scope.setTheme = function(newTheme){
            console.log(newTheme);
            path = '/theme/' + newTheme;
            $http.get(path, {timeout:5000})
                    .then(function(res)
                    {});
            $scope.theme = newTheme;

        };
      });

})();