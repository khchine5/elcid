angular.module('opal.controllers')
    .controller('DiagnosisAddEpisodeCtrl', function($scope, $http, $cookieStore, $q,
                                                    $timeout, $modal,
                                                    $modalInstance, Episode,
                                                    options,
                                                    demographics) {
        var DATE_FORMAT = 'DD/MM/YYYY';

        $scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
        $scope.currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

        for (var name in options) {
            $scope[name + '_list'] = options[name];
        };

        $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
        // TODO - this is no longer the way location/admission date works.
        $scope.editing = {
            tagging: [{}],
            location: {
                hospital: 'UCLH'
            },
            demographics: demographics
        };

        $scope.editing.tagging[0][$scope.currentTag] = true;
        if($scope.currentSubTag != 'all'){
            $scope.editing.tagging[0][$scope.currentSubTag] = true;
        }

        $scope.showSubtags = function(withsubtags){
            var show =  _.some(withsubtags, function(tag){
                return $scope.editing.tagging[0][tag]
            });
            return show
        };

        $scope.save = function() {
	    var dob, doa;

	    // This is a bit mucky but will do for now
	    doa = $scope.editing.date_of_admission;
	    if (doa) {
                if(!angular.isString(doa)){
                    doa = moment(doa).format(DATE_FORMAT);
                }
		$scope.editing.date_of_admission = doa;
	    }

	    dob = $scope.editing.demographics.date_of_birth;
	    if (dob) {
                if(!angular.isString(dob)){
                    dob = moment(dob).format(DATE_FORMAT);
                }
            }
	    $scope.editing.demographics.date_of_birth = dob;

            // TODO: Un-hard code this as part of elcid#192
            if($scope.editing.tagging[0].opat){
                $scope.editing.tagging[0].opat_referrals = true;
            }

            $http.post('episode/', $scope.editing).success(function(episode) {
                $scope.episode = new Episode(episode);
                $scope.presenting_complaint();
            });
        };

        $scope.presenting_complaint = function() {
            var deferred = $q.defer();
            $modalInstance.close(deferred.promise);

            var item = $scope.episode.newItem('presenting_complaint');
            $scope.episode.presenting_complaint[0] = item;
            modal = $modal.open({
                templateUrl: '/templates/modals/presenting_complaint.html/',
                controller: 'EditItemCtrl',
                size: 'lg',
                resolve: {
                    item: function() { return item; },
                    options: function() { return options; },
                    episode: function() { return $scope.episode; },
                    profile: function(UserProfile) { return UserProfile }
                }
            }).result.then(
                function(){deferred.resolve($scope.episode)},
                function(){deferred.resolve($scope.episode)}
            );
        };

        $scope.cancel = function() {
            $modalInstance.close(null);
        };

    });
