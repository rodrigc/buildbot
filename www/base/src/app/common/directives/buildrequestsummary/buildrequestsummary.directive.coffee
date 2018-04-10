class Buildrequestsummary
    constructor: (RecursionHelper) ->
        return {
            replace: true
            restrict: 'E'
            scope: {buildrequestid: '=?'}
            templateUrl: 'views/buildrequestsummary.html'
            compile: RecursionHelper.compile
            controller: '_buildrequestsummaryController'
        }

class _buildrequestsummary
    constructor: ($scope, dataService, buildersService, findBuilds, resultsService) ->
        _.mixin($scope, resultsService)
        $scope.$watch "buildrequest.claimed", (n, o) ->
            if n  # if it is unclaimed, then claimed, we need to try again
                findBuilds $scope,
                    $scope.buildrequest.buildrequestid

        data = dataService.open().closeOnDestroy($scope)
        data.getBuildrequests($scope.buildrequestid).onNew = (buildrequest) ->
            $scope.buildrequest = buildrequest
            data.getBuildsets(buildrequest.buildsetid).onNew = (buildset) ->
                $scope.buildset = buildset

            $scope.builder = buildersService.getBuilder(buildrequest.builderid)


angular.module('common')
.directive('buildrequestsummary', ['RecursionHelper', Buildrequestsummary])
.controller('_buildrequestsummaryController', ['$scope', 'dataService', 'buildersService', 'findBuilds', 'resultsService', _buildrequestsummary])