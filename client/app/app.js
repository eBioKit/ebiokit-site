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
*  - MainController
*/

(function() {

	var app = angular.module('eBioKitMainSiteApp', [
		'ang-dialogs',
		'ui.router',
		'ngSanitize',
		'services.directives.service-directives',
		'services.controllers.service-list'
	]);

	app.constant('myAppConfig', {
		VERSION: '18.10',
		SERVER_URL : "/"
	});

	//Define the events that are fired in the APP
	app.constant('APP_EVENTS', {
		launchService: 'launch-service'
	});

	//DEFINE THE ENTRIES FOR THE WEB APP
	app.config([
		'$stateProvider',
		'$urlRouterProvider',
		function ($stateProvider, $urlRouterProvider) {
			// For any unmatched url, redirect to /login
			$urlRouterProvider.otherwise("/home");
			var home = {
				name: 'home',
				url: '/',
				//templateUrl: "static/app/home/templates/home.tpl.html",
				data: {requireLogin: false}
			};
			$stateProvider.state(home);
		}]
	);


	/******************************************************************************
	*       _____ ____  _   _ _______ _____   ____  _      _      ______ _____   _____
	*      / ____/ __ \| \ | |__   __|  __ \ / __ \| |    | |    |  ____|  __ \ / ____|
	*     | |   | |  | |  \| |  | |  | |__) | |  | | |    | |    | |__  | |__) | (___
	*     | |   | |  | | . ` |  | |  |  _  /| |  | | |    | |    |  __| |  _  / \___ \
	*     | |___| |__| | |\  |  | |  | | \ \| |__| | |____| |____| |____| | \ \ ____) |
	*      \_____\____/|_| \_|  |_|  |_|  \_\\____/|______|______|______|_|  \_\_____/
	*
	******************************************************************************/
	app.controller('MainController', function ($rootScope, $scope, $state, $http, $sce, $timeout, myAppConfig, APP_EVENTS) {
		/******************************************************************************
		*       ___ ___  _  _ _____ ___  ___  _    _    ___ ___
		*      / __/ _ \| \| |_   _| _ \/ _ \| |  | |  | __| _ \
		*     | (_| (_) | .` | | | |   / (_) | |__| |__| _||   /
		*      \___\___/|_|\_| |_|_|_|_\\___/|____|____|___|_|_\
		*        | __| | | | \| |/ __|_   _|_ _/ _ \| \| / __|
		*        | _|| |_| | .` | (__  | |  | | (_) | .` \__ \
		*        |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|___/
		*
		******************************************************************************/

		$rootScope.getRequestPath = function(service, extra){
			extra = (extra || "");
			switch (service) {
				case "system-version":
				return myAppConfig.SERVER_URL + "api/system/version/";
				case "service-list":
				return myAppConfig.SERVER_URL + "api/applications/";
				case "service-info":
				return myAppConfig.SERVER_URL + "api/applications/info";
				default:
				return "";
			}
		};

		$rootScope.getHttpRequestConfig = function(method, service, options){
			options = (options || {});
			options.params = (options.params || {});

			var requestData = {
				method: method,
				headers: options.headers,
				url: this.getRequestPath(service, options.extra),
				params: options.params,
				data: options.data
			};

			if(options.transformRequest !== undefined){
				requestData.transformRequest = options.transformRequest;
			}

			return requestData;
		};

		this.setPage = function (page) {
			$state.transitionTo(page);
			$scope.currentPage = page;
		};

		this.getPageTitle  = function(page){
			return
		};

		this.setCurrentPageTitle = function(page){
			$scope.currentPageTitle = page;
		};

		this.retrieveSystemVersion = function(){
			$http($rootScope.getHttpRequestConfig("GET", "system-version", {})).
			then(
				function successCallback(response){
					$rootScope.systemVersion = response.data.system_version;
				},
				function errorCallback(response){
					$scope.isLoading = false;

					debugger;
					var message = "Failed while retrieving the system version.";
					$dialogs.showErrorDialog(message, {
						logMessage : message + " at AdminController:retrieveSystemVersion."
					});
					console.error(response.data);
				}
			);
		};

		this.getVisibleWindowsSize = function(){
			var n = Math.min($scope.visible_services.length, $scope.max_visible_services);
			if(n > 2){
				//TODO: IF N=3 SHOW BIGGER BASED ON THE ORDER IN THE ARRAY
				return "halfHeightDiv col-lg-6 col-md-6 col-sm-6"
			} else if(n === 2){
				return "halfHeightDiv col-lg-12 col-md-12 col-sm-12"
			}else {
				return "fullHeightDiv col-lg-12 col-md-12 col-sm-12"
			}
		};

		this.trustAsResourceUrl = function(service) {
			return $sce.trustAsResourceUrl(this.getLinkToService(service));
		};

		this.getLinkToService = function(service){
			//if it is a ip address
			if (service.port && (document.location.hostname === "localhost" || /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(document.location.hostname))){
				var port  = service.port.split(",")[0];
				return document.location.origin.replace(new RegExp(":" + document.location.port + "$"), "")  + ":" + port;
			}else if(service.website != null || service.website !== ""){
				return service.website;
			}else{
				return "/not-found.html";
			}
		};

		this.getServiceByName = function(name){
			for(var i in $scope.open_services){
				if($scope.open_services[i].name === name){
					return $scope.open_services[i];
				}
			}
		};

		/******************************************************************************
		*            _____   _____ _  _ _____
		*           | __\ \ / / __| \| |_   _|
		*           | _| \ V /| _|| .` | | |
		*      _  _ |___| \_/_|___|_|\_| |_| ___  ___
		*     | || | /_\ | \| |   \| |  | __| _ \/ __|
		*     | __ |/ _ \| .` | |) | |__| _||   /\__ \
		*     |_||_/_/ \_\_|\_|___/|____|___|_|_\|___/
		*
		******************************************************************************/
		$scope.$on(APP_EVENTS.launchService, function (event, args) {
			me.launchServiceHandler(args);
			me.changeCurrentServiceHandler(args);
		});

		this.launchServiceHandler = function(service){
			if($scope.open_services.indexOf(service) === -1){
				$scope.open_services.push(service);
			}
			$scope.displayOptions.showMenu = false;
		};

		this.changeCurrentServiceHandler = function(service){
			if($scope.visible_services.indexOf(service) === -1){
				if($scope.visible_services.length >=  $scope.max_visible_services){
					$scope.visible_services.shift();
				}
				$scope.visible_services.push(service);
				$scope.service_window_size = this.getVisibleWindowsSize();
			}
		};

		this.setMaxVisibleServicesHandler = function(nServices){
			if(nServices > 0 && nServices < 5){
				$scope.max_visible_services = nServices;
				while($scope.visible_services.length >  $scope.max_visible_services){
					$scope.visible_services.shift();
				}
				$scope.service_window_size = this.getVisibleWindowsSize();
			}
		};

		this.closeServiceHandler = function(service){
			this.hideServiceHandler(service);
			if(service.name !== "home"){
				var pos = $scope.open_services.indexOf(service);
				if(pos !== -1){
					$scope.open_services.splice(pos, 1);
				}
			}
		};

		this.hideServiceHandler = function(service){
			var pos = $scope.visible_services.indexOf(service);
			if(pos !== -1){
				$scope.visible_services.splice(pos, 1);
			}
			if($scope.visible_services.length === 0){
				//show home
				this.changeCurrentServiceHandler(this.getServiceByName("home"));
			}else{
				$scope.service_window_size = this.getVisibleWindowsSize();
			}
		};

		this.displayApplicationMenuHandler = function(){
			$scope.displayTimeout = $timeout(function(){
				$scope.displayOptions.showMenu = true;
			},3000);
		};

		this.displayApplicationMenuClickHandler = function(){
			$scope.displayOptions.showMenu = !$scope.displayOptions.showMenu;
		};

		this.cancelDisplayApplicationMenuHandler = function(){
			if($scope.displayTimeout !== undefined){
				$timeout.cancel($scope.displayTimeout);
				delete $scope.displayTimeout;
			}
		};

		this.uncollapseMenuHandler = function(){
			$scope.uncollapseTimeout = $timeout(function(){
				$scope.collapsedBar = 'expanded';
			},2000);
		};

		this.collapseMenuHandler = function(){
			if($scope.uncollapseTimeout !== undefined){
				$timeout.cancel($scope.uncollapseTimeout);
				delete $scope.uncollapseTimeout;
			}
			$scope.collapsedBar = '';;
		};


		/******************************************************************************
		*      ___ _  _ ___ _____ ___   _   _    ___ ____  _ _____ ___ ___  _  _
		*     |_ _| \| |_ _|_   _|_ _| /_\ | |  |_ _|_  / /_\_   _|_ _/ _ \| \| |
		*      | || .` || |  | |  | | / _ \| |__ | | / / / _ \| |  | | (_) | .` |
		*     |___|_|\_|___| |_| |___/_/ \_\____|___/___/_/ \_\_| |___\___/|_|\_|
		*
		******************************************************************************/
		var me = this;
		$rootScope.myAppConfig = myAppConfig;

		$scope.displayOptions = {
			showMenu: false
		};

		$scope.open_services = [
			{name:"home", title: 'Home page', description: 'The main eBioKit page', website : '/home'}
		];

		$scope.visible_services = [$scope.open_services[0]];
		$scope.max_visible_services = 1;
		$scope.service_window_size = this.getVisibleWindowsSize();

		this.retrieveSystemVersion();

	});
})();
