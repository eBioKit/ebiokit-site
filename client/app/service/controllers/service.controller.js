/*
* (C) Copyright 2017 SLU Global Bioinformatics Centre, SLU
* (http://sgbc.slu.se) and the eBioKit Project (http://ebiokit.eu).
*
* This file is part of The eBioKit portal 2017. All rights reserved.
* The eBioKit portal is free software: you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation, either version 3 of
* the License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
* Lesser General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with eBioKit portal.  If not, see <http://www.gnu.org/licenses/>.
*
* Contributors:
*     Dr. Erik Bongcam-Rudloff
*     Dr. Rafael Hernandez de Diego (main developer)
*     and others.
*
*  More info http://ebiokit.eu/
*  Technical contact ebiokit@gmail.com
*
* THIS FILE CONTAINS THE FOLLOWING MODULE DECLARATION
* - ServiceListController
* -
*
*/
(function(){
	var app = angular.module('services.controllers.service-list', [
		'ui.bootstrap',
		'ang-dialogs',
		'services.services.service-list'
	]);

	app.controller('ServiceListController', function($rootScope, $scope, $http, $uibModal, $dialogs, APP_EVENTS, ServiceList) {
		//--------------------------------------------------------------------
		// CONTROLLER FUNCTIONS
		//--------------------------------------------------------------------
		this.retrieveServicesListData = function(force){
			$scope.isLoading = true;

			if(ServiceList.getOld() > 1 || force){ //Max age for data 5min.
				$http($rootScope.getHttpRequestConfig("GET", "service-list", {}))
				.then(
					function successCallback(response){
						$scope.isLoading = false;
                        debugger
						$scope.services = ServiceList.setServices(response.data.data).getServices();
						$scope.categories = ServiceList.updateCategories().getCategories();
						if($scope.categories.length > 0){
							$scope.categoryFilter=[$scope.categories[0].name];
						}
					},
					function errorCallback(response){
						$scope.isLoading = false;

						debugger;
						var message = "Failed while retrieving the services list.";
						$dialogs.showErrorDialog(message, {
							logMessage : message + " at ServiceListController:retrieveServicesListData."
						});
						console.error(response.data);
					}
				);
			}else{
				$scope.services = ServiceList.getServices();
				$scope.isLoading = false;
			}
		};


		/**
		* This function defines the behaviour for the "filterWorkflows" function.
		* Given a item (service) and a set of filters, the function evaluates if
		* the current item contains the set of filters within the different attributes
		* of the model.
		*
		* @returns {Boolean} true if the model passes all the filters.
		*/
		$scope.filterServices = function() {
			return function( item ) {
				if($scope.searchFor === undefined || $scope.searchFor === "" || $scope.searchFor.length < $scope.minSearchLength){
					return true;
				}
				return (item["title"].toLowerCase().indexOf($scope.searchFor.toLowerCase()) !== -1);
			};
		};

		/**
		* This function defines the behaviour for the "filterByCategory" function.
		*
		* @returns {Boolean} true if the model passes all the filters.
		*/
		$scope.filterServicesByCategory = function() {
			return function( item ) {
				var filterAux, item_categories;
				return ($scope.categoryFilter !== null) && item.enabled && (item["categories"].toLowerCase().indexOf($scope.categoryFilter[0].toLowerCase()) !== -1);
			};
		};
		//--------------------------------------------------------------------
		// EVENT HANDLERS
		//--------------------------------------------------------------------
		/**
		* This function applies the filters when the user clicks on "Search"
		*/
		// this.applySearchHandler = function() {
		// 	var filters = arrayUnique($scope.filters.concat($scope.searchFor.split(" ")));
		// 	$scope.filters = filters;
		// };

		this.launchServiceHandler = function(service){
			$rootScope.$broadcast(APP_EVENTS.launchService, service);
		};

		this.launchServiceHandler = function(service){
			$rootScope.$broadcast(APP_EVENTS.launchService, service);
		};

		$scope.getIconText = function(service_name){
			var text = service_name.split(" ");
			if(text.length > 1){
				return text[0][0].toUpperCase() + text[1][0].toLowerCase();
			}
			return text[0][0].toUpperCase() + text[0][1].toLowerCase();
		};

		this.displayHelpHandler = function(service){
			$scope.displayed_service = service;
			$scope.displayed_service_categories = service.categories.split(',');
			debugger
			$scope.modalInstance = $uibModal.open({
				controller: 'ServiceListController',
				controllerAs: 'controller',
				scope: $scope,
				backdrop : 'static',
				size:'md',
				template:
				'<div class="modal-header"><h3 class="modal-title">About {{displayed_service.title}}</h3></div>' +
				'<div class="modal-body">'+
				'	<div class="" style="">'+
				'	   <b>Categories:</b>'+
				'	   <div class="" style="">'+
				'	      <span ng-repeat="category in displayed_service_categories" class="label label-primary" style="margin-right: 5px;">{{category}}</span>'+
				'      </div>' +
				'	   <p style="margin-top: 10px;"><b>Instance name:</b>{{displayed_service.instance_name}}</p>'+
				'	   <p style="margin-top: 10px;"><b>Version:</b>{{displayed_service.version}}</p>'+
				'	   <b>Description:</b>'+
				'      <p style="margin-top: 10px;min-height:150px; border: 1px solid #dedede;">{{displayed_service.description}}</p>'+
				'   </div>' +
				// '      <b class="text-danger" >Invalid settings</b><br>Some settings are not valid or empty. Please check the form and try again.'+
				// '      <ul><li ng-repeat="setting in invalidSettings">{{setting}}</li></ul>' +
				// '   <div class="form-group" ng-repeat="setting in installSettings">' +
				// '     <label for="{{setting.name}}">{{setting.label}}: <i class="fa fa-question-circle text-info" data-toggle="tooltip" title="{{setting.description}}"></i></label>' +
				// '     <input type="{{setting.type}}" ng-model="setting.value" class="form-control" id="{{setting.name}}">' +
				// '   </div>' +
				'</div>' +
				'<div class="modal-footer">' +
				'	<a class="btn btn-danger" ng-click="controller.closeHelpDialogButtonHandler(\'cancel\')">Close</button>' +
				'</div>'
			});
		};

		this.closeHelpDialogButtonHandler = function(){
			$scope.modalInstance.close();
			delete $scope.modalInstance;
			delete $scope.displayed_service_categories;
			delete $scope.displayed_service;
	}

		//--------------------------------------------------------------------
		// INITIALIZATION
		//--------------------------------------------------------------------
		var me = this;
		$scope.services = ServiceList.getServices();
		$scope.minSearchLength = 2;
		$scope.categories =  ServiceList.getCategories();
		$scope.filters =  ServiceList.getFilters();
		$scope.filteredServices = $scope.services.length;
		$scope.categoryFilter = [];

		if($scope.services.length === 0){
			this.retrieveServicesListData(true);
		}
	});
})();
