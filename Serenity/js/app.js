(function () {

    var app = angular.module('SerenityApp', ['ngMaterial', 'ngMessages', 'material.svgAssetsCache', 'ngRoute', 'ngMdIcons']);
    app.config(function ($mdThemingProvider) {
        $mdThemingProvider.theme('default').accentPalette('lime');

        //$mdThemingProvider.theme('altTheme')
        //    .backgroundPalette('grey',{'default': '900'})
        //                .dark();
        $mdThemingProvider.theme('default-dark').accentPalette('lime').dark(true);
        $mdThemingProvider.theme('orange').primaryPalette('orange').accentPalette('grey', {'default': '400'});
        $mdThemingProvider.theme('orange-dark').primaryPalette('orange').accentPalette('grey', {'default': '600'}).dark(true);

        $mdThemingProvider.theme('blue').primaryPalette('blue').accentPalette('amber');
        $mdThemingProvider.theme('blue-dark').primaryPalette('blue').accentPalette('amber').dark(true);

        $mdThemingProvider.theme('cyan').primaryPalette('cyan').accentPalette('deep-purple');
        $mdThemingProvider.theme('cyan-dark').primaryPalette('cyan').accentPalette('deep-purple').dark(true);

        $mdThemingProvider.theme('green').primaryPalette('light-green').accentPalette('yellow');
        $mdThemingProvider.theme('green-dark').primaryPalette('light-green').accentPalette('yellow').dark(true);

        $mdThemingProvider.theme('red').primaryPalette('red').accentPalette('light-blue');
        $mdThemingProvider.theme('red-dark').primaryPalette('red').accentPalette('light-blue').dark(true);

        //$mdThemingProvider.setDefaultTheme('altTheme');
        $mdThemingProvider.alwaysWatchTheme(true);
    });

    app.controller('SerenityCtrl', function ($scope, $timeout, $mdSidenav, $log, $http, $location) {
        $scope.toggleLeft = buildDelayedToggler('left');
        $scope.toggleRight = buildToggler('right');
        $scope.isOpenRight = function () {
            return $mdSidenav('right').isOpen();
        };


        $scope.menuItems = [
            {
                link: '/',
                title: 'Dashboard',
                icon: 'dashboard'
            }
        ];
        $scope.adminItems = [
            {
                link: '/settings',
                title: 'Settings',
                icon: 'settings'
            }
        ];

        $scope.changeLocation = function (location) {
            console.log('Chnage Location')
            $location.path(location)
        };

        $http.get('/theme', {timeout: 5000})
            .then(function (res) {
                $scope.theme = res.data;
                console.log($scope.theme)
            });

        $scope.themes = ['default', 'default-dark', 'orange', 'orange-dark', 'blue', 'blue-dark', 'cyan', 'cyan-dark',
            'green', 'green-dark', 'red', 'red-dark'];

        $scope.$watch('selectedTheme', function (value) {
            if (value != undefined) {
                $scope.theme = value;
                console.log('Changed theme', $scope.theme, value);
                path = '/theme/' + value;
                $http.get(path, {timeout: 5000})
                    .then(function (res) {
                    });
            }
        });


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
                timer = $timeout(function () {
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
            return debounce(function () {
                $mdSidenav(navID)
                    .toggle()
                    .then(function () {
                        $log.debug("toggle " + navID + " is done");
                    });
            }, 200);
        }

        function buildToggler(navID) {
            return function () {
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

    app.config(['$routeProvider',
        function ($routeProvider) {
            $routeProvider.when('/', {
                templateUrl: '/tpl/sample.html',
            }).when('/settings', {
                templateUrl: '/tpl/settings.html',
            }).otherwise({
                redirectTo: '/'
            });
        }])


})();