
(function () {

    var app = angular.module('SerenityApp', ['ngMaterial', 'material.svgAssetsCache'])
        .config(function($mdThemingProvider) {
            $mdThemingProvider.theme('default').dark();

            //$mdThemingProvider.theme('altTheme')
            //    .backgroundPalette('grey',{'default': '900'})
            //                .dark();
            $mdThemingProvider.theme('altTheme').warnPalette('blue').dark(false);

            //$mdThemingProvider.setDefaultTheme('altTheme');
            $mdThemingProvider.alwaysWatchTheme(true);
        });

    app.controller('SerenityCtrl', function($scope, $timeout, $mdSidenav, $log)
    {
        $scope.dynamicTheme = 'altTheme';
        $scope.myFunction = function()
        {
            console.log("This");
            console.log($scope.dynamicTheme);

        };
    });
})();