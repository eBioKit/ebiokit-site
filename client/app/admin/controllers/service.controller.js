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
(function() {
  var app = angular.module('admin.controllers.service-list', [
    'ui.bootstrap',
    'ang-dialogs',
    'chart.js',
    'ngCookies',
    'services.services.service-list',
    'jobs.services.job-list'
  ]);

  app.controller('ServiceListController', function($rootScope, $scope, $http, $dialogs, $state, $interval, APP_EVENTS, ServiceList) {
    //--------------------------------------------------------------------
    // CONTROLLER FUNCTIONS
    //--------------------------------------------------------------------
    this.retrieveServicesListData = function(force, callback_caller, callback_function) {
      $scope.isLoading = true;

      if (ServiceList.getOld() > 1 || force) { //Max age for data 5min.
        $http($rootScope.getHttpRequestConfig("GET", "service-list", {})).
        then(
          function successCallback(response) {
            $scope.isLoading = false;
            $scope.services = ServiceList.setServices(response.data).getServices();
            $scope.categories = ServiceList.updateCategories().getCategories();

            if (callback_function !== undefined) {
              callback_caller[callback_function]();
            }
          },
          function errorCallback(response) {
            $scope.isLoading = false;

            debugger;
            var message = "Failed while retrieving the services list.";
            $dialogs.showErrorDialog(message, {
              logMessage: message + " at ServiceListController:retrieveServicesListData."
            });
            console.error(response.data);
          }
        );
      } else {
        $scope.services = ServiceList.getServices();
        $scope.isLoading = false;
      }
    };

    this.retrieveSystemInfo = function() {
      $http($rootScope.getHttpRequestConfig("GET", "system-info", {})).
      then(
        function successCallback(response) {
          $scope.mem_load = [
            [response.data.mem_use]
          ];
          $scope.swap_use = [
            [response.data.swap_use]
          ];
          $scope.cpu_loads[0].push(response.data.cpu_use);
          $scope.cpu_loads[0].shift();
        },
        function errorCallback(response) {
          $scope.isLoading = false;
          debugger;
          var message = "Failed while retrieving the system information.";
          $dialogs.closeDialog("error");
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:retrieveSystemInfo."
          });
          console.error(response.data);
        }
      );
    };

    this.updateServicesInfo = function() {
      console.log("Updating service information");
      me.retrieveServicesListData(true);
    };

    this.checkAvailableUpdates = function() {
      debugger
      $scope.isLoading = true;

      $http($rootScope.getHttpRequestConfig("GET", "available-updates", {})).
      then(
        function successCallback(response) {
          $scope.isLoading = false;
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while checking the available updates.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:checkAvailableUpdates."
          });
          console.error(response.data);
        }
      );
    };

    this.retrieveAvailableApplications = function() {
      $scope.isLoading = true;

      $http($rootScope.getHttpRequestConfig("GET", "available-applications", {})).
      then(
        function successCallback(response) {
          $scope.isLoading = false;
          $scope.services = ServiceList.updateServices(response.data["available_apps"]).getServices();
          $scope.categories = ServiceList.updateCategories().getCategories();
          $scope.repository_name = response.data.repository_name;
          $scope.repository_url = response.data.repository_url;
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while checking the available applications.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:checkAvailableApplications."
          });
          console.error(response.data);
        }
      );
    };

    this.retrieveSystemSettings = function() {
      var me = this;
      $http($rootScope.getHttpRequestConfig("GET", "system-settings", {})).
      then(
        function successCallback(response) {
          $scope.settings = response.data.settings;
          for (var i in $scope.settings.available_remote_servers) {
            if ($scope.settings.available_remote_servers[i].url === $scope.settings.remote_server.url) {
              $scope.settings.remote_server = $scope.settings.available_remote_servers[i];
            }
          }
          me.retrieveSystemVersion();
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while retrieving the system settings.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:retrieveSystemSettings."
          });
          console.error(response.data);
        }
      );
    };

    this.retrieveSystemVersion = function() {
      $http($rootScope.getHttpRequestConfig("GET", "system-version", {})).
      then(
        function successCallback(response) {
          $scope.settings.latest_version = "" + response.data.latest_version;
          $scope.settings.system_version = "" + response.data.system_version;
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while retrieving the system version.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:retrieveSystemVersion."
          });
          console.error(response.data);
        }
      );
    };
    /**
     * This function defines the behaviour for the "filterServices" function.
     * Given a item (service) and a set of filters, the function evaluates if
     * the current item contains the set of filters within the different attributes
     * of the model.
     *
     * @returns {Boolean} true if the model passes all the filters.
     */
    $scope.filterServices = function() {
      $scope.filteredServices = 0;
      return function(item) {
        if ($scope.displayServices === "installed" && item.installed === undefined) {
          return false;
        } else if ($scope.displayServices === "updates" && item.categories.indexOf(",updatable") === -1) {
          return false;
        } else if ($scope.displayServices === "all" && item.installed) {
          return false;
        }

        var filterAux, item_tags;
        for (var i in $scope.filters) {
          filterAux = $scope.filters[i].toLowerCase();
          if (!((item.title.toLowerCase().indexOf(filterAux)) !== -1 || (item.description.toLowerCase().indexOf(filterAux)) !== -1 || (item.categories.toLowerCase().indexOf(filterAux)) !== -1)) {
            return false;
          }
        }
        $scope.filteredServices++;
        return true;

      };
    };

    //--------------------------------------------------------------------
    // EVENT HANDLERS
    //--------------------------------------------------------------------
    /**
     * This function applies the filters when the user clicks on "Search"
     */
    this.applySearchHandler = function() {
      var filters = [];
      for (var i in $scope.categories) {
        if ($scope.categories[i].selected) {
          filters.push($scope.categories[i].name);
        }
      }
      if ($scope.searchFor !== "") {
        filters = arrayUnique(filters.concat($scope.searchFor.split(" ")));
      }
      $scope.searchFor = "";
      $scope.filters = ServiceList.setFilters(filters).getFilters();
    };

    this.clickCategorySelectorHandler = function(category) {
      category.selected = !(category.selected === true);
      this.applySearchHandler();
    };

    /******************************************************************************
     * This function remove a given filter when the user clicks at the "x" button
     *
     * @param {String} filter the filter to be removed
     ******************************************************************************/
    this.removeFilterHandler = function(filter) {
      $scope.filters = ServiceList.removeFilter(filter).getFilters();
      for (var i in $scope.categories) {
        if ($scope.categories[i].name === filter) {
          $scope.categories[i].selected = false;
          return;
        }
      }
    };

    this.launchServiceHandler = function(service) {
      $rootScope.$broadcast(APP_EVENTS.launchService, service);
    };

    this.refreshStoreContent = function() {
      this.retrieveServicesListData(true, this, "retrieveAvailableApplications");
    };

    this.updateUserPasswordHandler = function() {
        var valid = $scope.settings.password
        && $scope.settings.password.length > 7
        && $scope.settings.password === $scope.settings.passconfirm
        if ( valid ) {
            var me = this;
            $http($rootScope.getHttpRequestConfig("POST", "user-password", {
                data: {
                    "password": $scope.settings.password
                }
            })).
            then(
                function successCallback(response) {
                    response = response.data;
                    if (response.success === true) {
                        $dialogs.showSuccessDialog("Password was succesfully update.");
                    } else {
                        $scope.errorPasswordsMessage = response.other.error_message
                        return;
                    }
                },
                function errorCallback(response) {
                    if (response.data && [404001].indexOf(response.data.err_code) !== -1) {
                        $dialogs.showErrorDialog("Invalid user or password.");
                        return;
                    }
                    debugger;
                    var message = "Failed while updating the user's password.";
                    $dialogs.showErrorDialog(message, {
                        logMessage: message + " at ServiceListController:updateUserPasswordHandler."
                    });
                    console.error(response.data);
                    }
            );
        } else if(! $scope.settings.password){
            $scope.errorPasswordsMessage = "Password can not be empty."
        } else if($scope.settings.password !== $scope.settings.passconfirm){
            $scope.errorPasswordsMessage = "Passwords do not match."
        } else if($scope.settings.password.length <= 7){
            $scope.errorPasswordsMessage = "Password must contain at least 8 characters (one upper case, one number and no spaces)."
        };
    };

    this.isNewerVersion = function(old_version, new_version) {
        if(! old_version || ! new_version){
            return false;
        }
        const oldParts = old_version.split('.')
        const newParts = new_version.split('.')
        for (var i = 0; i < newParts.length; i++) {
            const a = ~~newParts[i] // parse int
            const b = ~~oldParts[i] // parse int
            if (a > b) return true
            if (a < b) return false
        }
        return false
    }

    this.updateSystemSettingsHandler = function() {
      if ($scope.prev_password === "" || $scope.settings.password !== $scope.settings.password2) {
        return;
      }

      delete $scope.settings.invalid_prev_pass;
      var me = this;
      $http($rootScope.getHttpRequestConfig("POST", "system-settings", {
        data: {
          "settings": $scope.settings
        }
      })).
      then(
        function successCallback(response) {
          $dialogs.showSuccessDialog("Settings were succesfully created. You may need to log out and log in again to see the changes.");
          me.retrieveSystemSettings();
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          if (response.data.err_code === 404001) {
            $scope.settings.invalid_prev_pass = true;
            return;
          }

          debugger;
          var message = "Failed while saving the system settings.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceListController:updateSystemSettingsHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.onChangeSelectedRemoteServerHandler = function() {
      debugger
    }

    this.deleteRemoteServerHandler = function(remote_server) {
      for (var i in $scope.settings.available_remote_servers) {
        if ($scope.settings.available_remote_servers[i] === remote_server) {
          $scope.settings.available_remote_servers.splice(i, 1);
          if ($scope.settings.available_remote_servers.length > 0) {
            $scope.settings.remote_server = $scope.settings.available_remote_servers[0];
          } else {
            delete $scope.settings.remote_server;
          }
        }
      }
    }

    this.addNewRemoteServerHandler = function() {
      var new_elem = {
        "name": "New server " + ($scope.settings.available_remote_servers.length + 1),
        url: ""
      };
      $scope.settings.available_remote_servers.push(new_elem);
      $scope.settings.remote_server = new_elem;
    }

    this.showServicesShopHandler = function() {
      $rootScope.$broadcast(APP_EVENTS.installNewServiceAction);
    }

    //--------------------------------------------------------------------
    // INITIALIZATION
    //--------------------------------------------------------------------
    var me = this;
    $scope.services = ServiceList.getServices();
    $scope.minSearchLength = 2;
    $scope.searchFor = "";
    $scope.categories = ServiceList.getCategories();
    $scope.filters = ServiceList.getFilters();
    $scope.filteredServices = $scope.services.length;

    if ($state.current.name === "control-panel") {
      this.retrieveServicesListData(true);
      this.retrieveSystemInfo();
      $scope.interval.push($interval(this.retrieveSystemInfo, 5000));
      $scope.interval.push($interval(this.updateServicesInfo, 30000));

      $scope.cpu_loads = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      ];
      $scope.cpu_load_labels = ["", "", "", "", "", "", "", "", "", ""];
      $scope.cpu_colors = [{
        backgroundColor: 'rgba(249,130,155,0.2)',
        pointBackgroundColor: 'rgba(249,130,155,1)',
        borderColor: 'rgba(249,130,155,1)',
        pointBorderColor: '#fff',
        pointHoverBorderColor: 'rgba(148,159,177,0.8)'
      }];
      $scope.cpu_options = {
        title: {
          display: true,
          text: 'CPU usage (%)'
        },
        animation: {
          duration: 0
        },
        tooltips: {
          enabled: false
        },
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            display: false
          }],
          yAxes: [{
            type: 'linear',
            ticks: {
              max: 100,
              min: 0
            }
          }]
        }
      };

      $scope.mem_load = [
        [0]
      ];
      $scope.mem_options = {
        animation: {
          duration: 500
        },
        title: {
          display: true,
          text: 'Mem usage (%)'
        },
        tooltip: {
          enabled: false
        },
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            type: 'linear',
            ticks: {
              max: 100,
              min: 0
            }
          }]
        }
      };
      $scope.swap_use = [
        [0]
      ];
      $scope.swap_options = {
        animation: {
          duration: 500
        },
        tooltip: {
          enabled: false
        },
        title: {
          display: true,
          text: 'Swap usage (%)'
        },
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            type: 'linear',
            ticks: {
              max: 100,
              min: 0
            }
          }]
        }
      };
    } else if ($state.current.name === "application-store") {
      this.retrieveServicesListData(true, this, "retrieveAvailableApplications");
      $scope.displayServices = 'installed';
      // $scope.interval.push($interval(function(){
      // 	me.retrieveServicesListData(true, me, "retrieveAvailableApplications");
      // }, 15000));
    } else if ($state.current.name === "settings") {
      this.retrieveSystemSettings();
    }
  });

  app.controller('ServiceController', function($rootScope, $scope, $http, $uibModal, $dialogs, APP_EVENTS, ServiceList) {
    //--------------------------------------------------------------------
    // CONTROLLER FUNCTIONS
    //--------------------------------------------------------------------
    this.checkServiceStatus = function(service) {
      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Checking status";

      $http($rootScope.getHttpRequestConfig("GET", "service-status", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          service.status = response.data.status;
          service.status_msg = response.data.status_msg;
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while retrieving the service status.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:checkServiceStatus."
          });
          console.error(response.data);
        }
      );
    };

    this.getLinkToService = function(service) {
      //if it is a ip address
      if (service.port !== undefined) {
        if (document.location.hostname === "localhost" || /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(document.location.hostname)) {
          var port = service.port.split(",")[0];
          return document.location.origin.replace(":" + document.location.port, "") + ":" + port;
        } else if (service.website != null || service.website !== "") {
          return service.website;
        }
      }
      return "/not-found.html";
    };

    this.autogenerateValue = function() {
      return Math.random().toString(36).slice(-8) + Math.random().toString(36).slice(-8);
    };

    //--------------------------------------------------------------------
    // EVENT HANDLERS
    //--------------------------------------------------------------------

    this.stopServiceHandler = function(service) {
      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Stopping service";

      $http($rootScope.getHttpRequestConfig("POST", "service-stop", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          me.checkServiceStatus(service);
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while stopping the service.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:stopService."
          });
          console.error(response.data);
        }
      );
    };

    this.startServiceHandler = function(service) {
      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Starting service";

      $http($rootScope.getHttpRequestConfig("POST", "service-start", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          me.checkServiceStatus(service);
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while starting the service.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:startService."
          });
          console.error(response.data);
        }
      );
    };

    this.restartServiceHandler = function(service) {
      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Restarting service";

      $http($rootScope.getHttpRequestConfig("POST", "service-restart", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          me.checkServiceStatus(service);
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while restarting the service.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:restartService."
          });
          console.error(response.data);
        }
      );
    };

    this.disableServiceHandler = function(service) {
      if(service.status != 'STOPPED'){
        service.status_msg = "Please, stop service before disable."
        return;
      }

      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Disabling service";

      $http($rootScope.getHttpRequestConfig("GET", "service-disable", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          service.enabled = response.data.enabled;
          me.checkServiceStatus(service);
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while disabling the service.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:disableServiceHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.enableServiceHandler = function(service) {
      delete service.status;
      delete service.status_msg;
      $scope.current_action = "Enabling service";

      $http($rootScope.getHttpRequestConfig("GET", "service-enable", {
        extra: service.instance_name
      })).then(
        function successCallback(response) {
          service.enabled = response.data.enabled;
          me.checkServiceStatus(service);
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while enabling the service.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:enableServiceHandler."
          });
          console.error(response.data);
        }
      );
    };

    /**
     * This function retrieves the installation settings for the selected service
     * and displays a new dialog for configure the new service instance.
     * */
    this.installServiceHandler = function(service) {
      $http($rootScope.getHttpRequestConfig("GET", "service-prepare-install", {
        extra: service.name
      })).then(
        function successCallback(response) {
          //Generate the form with the installation options
          $scope.installSettings = response.data.settings;
          $scope.invalidSettings = [];
          $scope.service = service;
          $scope.invalidValues = response.data.invalid_options;

          //Open a new dialog
          $scope.modalInstance = $uibModal.open({
            controller: 'ServiceController',
            controllerAs: 'controller',
            scope: $scope,
            backdrop: 'static',
            template:
              ('<div class="modal-header"><h3 class="modal-title">Install new service</h3></div>' +
                '<div class="modal-body">' +
                '	<div class="well well-sm">Please, use the following form to configure your new instance.</div>' +
                '	<div class="well well-sm text-danger" style=" background-color: #ffefef; background-image: none; " ng-show="invalidSettings.length > 0">' +
                '      <b class="text-danger" >Invalid settings</b><br>Some settings are not valid or empty. Please check the form and try again.' +
                '      <ul><li ng-repeat="setting in invalidSettings">{{setting}}</li></ul>' +
                '   </div>' +
                '   <div class="form-group" ng-repeat="setting in installSettings">' +
                '     <label for="{{setting.name}}">{{setting.label}}: <i class="fa fa-question-circle text-info" data-toggle="tooltip" title="{{setting.description}}"></i></label>' +
                '     <input type="{{setting.type}}" ng-init="setting.value = (setting.default ===\'autogenerated\'? controller.autogenerateValue(): setting.default)" ng-model="setting.value" class="form-control" id="{{setting.name}}">' +
                '   </div>' +
                '</div>' +
                '<div class="modal-footer">' +
                '	<a class="btn btn-success" ng-click="controller.prepareInstallButtonHandler(\'ok\')">Install service</button>' +
                '	<a class="btn btn-danger" ng-click="controller.prepareInstallButtonHandler(\'cancel\')">Cancel</button>' +
                '</div>')
          });
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while getting the installation settings.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:installServiceHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.prepareInstallButtonHandler = function(option) {
      if (option === 'ok') {

        //First check if all settings are valid
        $scope.invalidSettings.length = 0;
        var instance_title = "";
        for (var i in $scope.installSettings) {
          if ($scope.installSettings[i].value === undefined || $scope.installSettings[i].value === "") {
            $scope.invalidSettings.push($scope.installSettings[i].label + " cannot be empty");
          } else if ($scope.installSettings[i].name === "INSTANCE_TITLE") {
            instance_title = $scope.installSettings[i].value;
            if ($scope.invalidValues.titles.indexOf($scope.installSettings[i].value) > -1) {
              $scope.invalidSettings.push("\"" + $scope.installSettings[i].value + "\" is being used by another service, please try a different title.");
            }
          } else if ($scope.installSettings[i].name.indexOf("INSTANCE_PORT_") > -1) {
            if ($scope.invalidValues.ports.indexOf("" + $scope.installSettings[i].value) > -1) {
              $scope.invalidSettings.push("Port " + $scope.installSettings[i].value + " is being used by another service, please try with a different port number.");
            } else if (isNaN($scope.installSettings[i].value) || $scope.installSettings[i].value < 999 || $scope.installSettings[i].value > 99999) {
              $scope.invalidSettings.push("\"" + $scope.installSettings[i].value + "\" is not a valid port number.");
            }
          } else if ($scope.installSettings[i].type === "email") {
            var pattern = /^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/;
            if (!$scope.installSettings[i].value.match(pattern)) {
              $scope.invalidSettings.push("\"" + $scope.installSettings[i].value + "\" is not a valid email address.");
            }
          }
        }
        //If there is any error, abort
        if ($scope.invalidSettings.length > 0) {
          return;
        }

        var instance_name = instance_title.toLowerCase().replace(/[^a-zA-Z0-9 ]/g, '').replace(/ /g, "-");
        if ($scope.invalidValues.instance_names.indexOf(instance_name) > -1) {
          var i = 1;
          instance_name += "_" + i;
          while ($scope.invalidValues.instance_names.indexOf(instance_name) > -1) {
            i++;
            instance_name = instance_name.slice(0, -1) + i;
          }
        }

        var aux = {};
        for (var i in $scope.installSettings) {
          aux[$scope.installSettings[i].name] = $scope.installSettings[i].value;
        }
        aux["INSTANCE_NAME"] = instance_name;
        $scope.installSettings = aux;

        //If settings are valid, we send the install request
        $http($rootScope.getHttpRequestConfig("POST", "service-install", {
          extra: $scope.service.name,
          data: {
            settings: $scope.installSettings
          }
        })).then(
          function successCallback(response) {
            if (response.data.success) {
              $dialogs.showInfoDialog("The selected service is being installed, check the progress at the Job queue panel.");
              $rootScope.$broadcast(APP_EVENTS.serviceStoreAction);
            } else {
              $dialogs.showErrorDialog("Installation failed. Reason: " + response.data.error_message);
            }
          },
          function errorCallback(response) {
            $scope.isLoading = false;

            debugger;
            var message = "Failed while sending install request.";
            $dialogs.showErrorDialog(message, {
              logMessage: message + " at ServiceController:prepareInstallButtonHandler."
            });
            console.error(response.data);
          }
        );
      }
      $scope.modalInstance.close();
      delete $scope.modalInstance;
      delete $scope.installSettings;
      delete $scope.invalidSettings;
      delete $scope.invalidValues;
      delete $scope.service;
    };

    this.upgradeServiceHandler = function(service, candidate_name) {
      $http($rootScope.getHttpRequestConfig("GET", "service-prepare-upgrade", {
        extra: service.instance_name,
        params: {
          "candidate": candidate_name
        }
      })).then(
        function successCallback(response) {
          //Generate the form with the installation options
          $scope.upgradeSettings = response.data.settings;
          $scope.invalidSettings = [];
          $scope.service = service;
          $scope.invalidValues = response.data.invalid_options;

          //Open a new dialog
          $scope.modalInstance = $uibModal.open({
            controller: 'ServiceController',
            controllerAs: 'controller',
            scope: $scope,
            backdrop: 'static',
            template:
              ('<div class="modal-header"><h3 class="modal-title">Upgrade service</h3></div>' +
                '<div class="modal-body">' +
                '	<div class="well well-sm">Please, use the following form to configure your instance.</div>' +
                '	<div class="well well-sm text-danger" style=" background-color: #ffefef; background-image: none; " ng-show="invalidSettings.length > 0">' +
                '      <b class="text-danger" >Invalid settings</b><br>Some settings are not valid or empty. Please check the form and try again.' +
                '      <ul><li ng-repeat="setting in invalidSettings">{{setting}}</li></ul>' +
                '   </div>' +
                '   <div class="form-group" ng-repeat="setting in upgradeSettings">' +
                '     <label for="{{setting.name}}">{{setting.label}}: <i class="fa fa-question-circle text-info" data-toggle="tooltip" title="{{setting.description}}"></i></label>' +
                '     <input type="{{setting.type}}" ng-init="setting.value = (setting.default ===\'autogenerated\'? controller.autogenerateValue(): setting.default)" ng-model="setting.value" class="form-control" id="{{setting.name}}">' +
                '   </div>' +
                '</div>' +
                '<div class="modal-footer">' +
                '	<a class="btn btn-success" ng-click="controller.prepareUpgradeButtonHandler(\'ok\', \'' + candidate_name + '\')">Upgrade service</button>' +
                '	<a class="btn btn-danger" ng-click="controller.prepareUpgradeButtonHandler(\'cancel\')">Cancel</button>' +
                '</div>')
          });
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while getting the upgrading settings.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at ServiceController:upgradeServiceHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.prepareUpgradeButtonHandler = function(option, candidate_name) {
      if (option === 'ok') {
        //First check if all settings are valid
        $scope.invalidSettings.length = 0;
        var instance_title = "";
        for (var i in $scope.upgradeSettings) {
          if ($scope.upgradeSettings[i].value === undefined || $scope.upgradeSettings[i].value === "") {
            $scope.invalidSettings.push($scope.upgradeSettings[i].label + " cannot be empty");
          } else if ($scope.upgradeSettings[i].name === "INSTANCE_TITLE") {
            instance_title = $scope.upgradeSettings[i].value;
            if ($scope.invalidValues.titles.indexOf($scope.upgradeSettings[i].value) > -1) {
              $scope.invalidSettings.push("\"" + $scope.upgradeSettings[i].value + "\" is being used by another service, please try a different title.");
            }
          } else if ($scope.upgradeSettings[i].name.indexOf("INSTANCE_PORT_") > -1) {
            if ($scope.invalidValues.ports.indexOf("" + $scope.upgradeSettings[i].value) > -1) {
              $scope.invalidSettings.push("Port " + $scope.upgradeSettings[i].value + " is being used by another service, please try with a different port number.");
            } else if (isNaN($scope.upgradeSettings[i].value) || $scope.upgradeSettings[i].value < 999 || $scope.upgradeSettings[i].value > 99999) {
              $scope.invalidSettings.push("\"" + $scope.upgradeSettings[i].value + "\" is not a valid port number.");
            }
          } else if ($scope.upgradeSettings[i].type === "email") {
            var pattern = /^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/;
            if (!$scope.upgradeSettings[i].value.match(pattern)) {
              $scope.invalidSettings.push("\"" + $scope.upgradeSettings[i].value + "\" is not a valid email address.");
            }
          }
        }
        //If there is any error, abort
        if ($scope.invalidSettings.length > 0) {
          return;
        }

        var instance_name = instance_title.toLowerCase().replace(/[^a-zA-Z0-9 ]/g, '').replace(/ /g, "-");
        if ($scope.invalidValues.instance_names.indexOf(instance_name) > -1) {
          var i = 1;
          instance_name += "_" + i;
          while ($scope.invalidValues.instance_names.indexOf(instance_name) > -1) {
            i++;
            instance_name = instance_name.slice(0, -1) + i;
          }
        }

        var aux = {};
        for (var i in $scope.upgradeSettings) {
          aux[$scope.upgradeSettings[i].name] = $scope.upgradeSettings[i].value;
        }
        aux["INSTANCE_NAME"] = instance_name;
        $scope.upgradeSettings = aux;

        //If settings are valid, we send the install request
        $http($rootScope.getHttpRequestConfig("POST", "service-upgrade", {
          extra: $scope.service.instance_name,
          data: {
            candidate: candidate_name,
            settings: $scope.upgradeSettings
          }
        })).then(
          function successCallback(response) {
            if (response.data.success) {
              $dialogs.showInfoDialog("The selected service is being upgraded, check the progress at the Job queue panel.");
              $rootScope.$broadcast(APP_EVENTS.serviceStoreAction);
            } else {
              $dialogs.showErrorDialog("Installation failed. Reason: " + response.data.error_message);
            }
          },
          function errorCallback(response) {
            $scope.isLoading = false;

            debugger;
            var message = "Failed while sending upgrade request.";
            $dialogs.showErrorDialog(message, {
              logMessage: message + " at ServiceController:prepareUpgradeButtonHandler."
            });
            console.error(response.data);
          }
        );
      }
      $scope.modalInstance.close();
      delete $scope.modalInstance;
      delete $scope.upgradeSettings;
      delete $scope.invalidSettings;
      delete $scope.invalidValues;
      delete $scope.service;
    };

    this.uninstallServiceHandler = function(service) {
      var uninstallWrapper = function(option) {
        if (option === 'ok') {
          $http($rootScope.getHttpRequestConfig("GET", "service-uninstall", {
            extra: service.instance_name
          })).then(
            function successCallback(response) {
              if (response.data.success) {
                $dialogs.showInfoDialog("The selected service is being uninstalled, check the progress at the Job queue panel.");
                $rootScope.$broadcast(APP_EVENTS.serviceStoreAction);
              } else {
                $dialogs.showErrorDialog("Uninstall has failed. Reason: " + response.data.error_message);
              }
            },
            function errorCallback(response) {
              $scope.isLoading = false;

              debugger;
              var message = "Failed while sending uninstall request.";
              $dialogs.showErrorDialog(message, {
                logMessage: message + " at ServiceController:uninstallServiceHandler."
              });
              console.error(response.data);
            }
          );
        }
      };

      $dialogs.showConfirmationDialog("If you uninstall this application, all the stored data and accounts will be removed from the system. Please confirm this action", {
        title: "Uninstall the application?",
        callback: uninstallWrapper
      });
    };
    //--------------------------------------------------------------------
    // INITIALIZATION
    //--------------------------------------------------------------------
    var me = this;

    if ($scope.service.installed && $scope.service.enabled && $scope.service.status === undefined) {
      this.checkServiceStatus($scope.service);
    }
  });

  app.controller('JobListController', function($rootScope, $scope, $http, $dialogs, $state, $interval, APP_EVENTS, JobList) {
    //--------------------------------------------------------------------
    // CONTROLLER FUNCTIONS
    //--------------------------------------------------------------------
    $scope.$on(APP_EVENTS.jobListChange, function(event, args) {
      me.retrieveJobsListData(true);
    });

    this.retrieveJobsListData = function(force, callback_caller, callback_function) {
      $scope.isLoading = true;
      if (JobList.getOld() > 1 || force) { //Max age for data 5min.
        $http($rootScope.getHttpRequestConfig("GET", "job-list", {})).
        then(
          function successCallback(response) {
            if(!response.data.success){
              $dialogs.closeDialog("error");
              $dialogs.showErrorDialog("Unable to get jobs status, reason: " + response.data.error_message, {
                logMessage: response.data.error_message + " at ServiceListController:retrieveJobsListData."
              });
            }
            $scope.isLoading = false;
            $scope.jobs = JobList.setJobs(response.data.jobs).getJobs();

            if (callback_function !== undefined) {
              callback_caller[callback_function]();
            }
          },
          function errorCallback(response) {
            $scope.isLoading = false;
            var message = "Failed while retrieving the jobs list.";
            $dialogs.closeDialog("error");
            $dialogs.showErrorDialog(message, {
              logMessage: message + " at ServiceListController:retrieveJobsListData."
            });
            console.error(response.data);
          }
        );
      } else {
        $scope.jobs = JobList.getJobs();
        $scope.isLoading = false;
      }
    };

    //--------------------------------------------------------------------
    // EVENT HANDLERS
    //--------------------------------------------------------------------

    //--------------------------------------------------------------------
    // INITIALIZATION
    //--------------------------------------------------------------------
    var me = this;

    if ($state.current.name === "jobs-queue") {
      $scope.expanded = {}
      this.retrieveJobsListData(true);
      while ($scope.interval.length > 0) {
        $interval.cancel($scope.interval[0]);
        $scope.interval.shift();
      }
      $scope.interval.push($interval(function() {
        me.retrieveJobsListData(true)
      }, 5000));
    }
  });

  app.controller('JobController', function($rootScope, $scope, $http, $dialogs, $cookies, $uibModal, APP_EVENTS, ServiceList) {
    //--------------------------------------------------------------------
    // CONTROLLER FUNCTIONS
    //--------------------------------------------------------------------

    //--------------------------------------------------------------------
    // EVENT HANDLERS
    //--------------------------------------------------------------------
    this.stopJobHandler = function(job) {

    };

    this.startJobHandler = function(job) {

    };

    this.restartJobHandler = function(job) {

    };

    this.removeJobHandler = function(job) {
      $dialogs.showWaitDialog("This process may take few seconds, be patient!");
      $http($rootScope.getHttpRequestConfig("DELETE", "job-list", {
        headers: {
          "X-CSRFToken": $cookies.get("csrftoken")
        },
        extra: job.id
      })).then(
        function successCallback(response) {
          $rootScope.$broadcast(APP_EVENTS.jobListChange);
          $dialogs.closeDialog();
        },
        function errorCallback(response) {
          $dialogs.closeDialog();
          $scope.isLoading = false;

          debugger;
          var message = "Failed while removing the job.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at JobController:removeJobHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.getJobLogHandler = function(job) {
      $rootScope.displayed_job = job;
      $rootScope.selected_task = job.tasks[0];

      //Open a new dialog
      $rootScope.modalInstance = $uibModal.open({
        controller: 'JobController',
        controllerAs: 'controller',
        backdrop: 'static',
        size: 'lg',
        template:
          ('<div class="modal-header"><h3 class="modal-title">Logs for tasks</h3></div>' +
            '<div class="modal-body">' +
            // '	<div class="well well-sm">Please, use the following form to configure your new instance.</div>' +
            ' <div class="tasks-logs">' +
            '   <div class="tasks-log">' +
            '     <h4>{{selected_task.id + " - " + selected_task.name}}</h4>' +
            '     <code ng-show="selected_task.log !== undefined">' +
            '       <p ng-repeat="line in selected_task.log">{{line}}</p>' +
            '     </code>' +
            '     <p ng-show="selected_task.log === undefined"><i class="fa fa-spinner fa-pulse fa-fw"></i> Loading...</p>' +
            '   </div>' +
            '   <div class="tasks-list">' +
            '     <b style="margin-bottom:5px;display: block;">Tasks in job {{displayed_job.id}}</b>' +
            '     <p style="margin-left: 8px;" ng-repeat="task in displayed_job.tasks" ng-class="(task.id === selected_task.id)?\'selected\':\'\'">' +
            '       <a class="clickable" ng-click="controller.getTaskLogHandler(task)">{{task.id + " - " + task.name}}</a>' +
            '     </p>' +
            '   </div>' +
            '</div>' +
            '<div class="modal-footer">' +
            '	<a class="btn btn-danger" ng-click="controller.closeJobLogDialogHandler()">Close</button>' +
            '</div>')
      });

      this.getTaskLogHandler($rootScope.selected_task);
    };

    this.getTaskLogHandler = function(task) {
      $rootScope.selected_task = task;

      $http($rootScope.getHttpRequestConfig("GET", "task-log", {
        extra: task.id
      })).then(
        function successCallback(response) {
          task.log = response.data.log.split("\n");
        },
        function errorCallback(response) {
          $scope.isLoading = false;

          debugger;
          var message = "Failed while getting the log content.";
          $dialogs.showErrorDialog(message, {
            logMessage: message + " at JobController:getTaskLogHandler."
          });
          console.error(response.data);
        }
      );
    };

    this.closeJobLogDialogHandler = function() {
      $rootScope.modalInstance.close();
      delete $rootScope.modalInstance;
      delete $rootScope.displayed_job;
    }

    $scope.getProgressBarClass = function() {
      if ($scope.job.status === 'Done') {
        return 'progress-bar-success';
      } else if ($scope.job.status === 'Failed') {
        return 'progress-bar-danger';
      }
      if ($scope.job.status === 'Waiting') {
        return 'progress-bar-info';
      } else {
        return 'progress-bar-info';
      }
    }

    $scope.formatJobDate = function(job) {
      return job.date.substr(6, 2) + "/" + job.date.substr(4, 2) + "/" + job.date.substr(0, 4) + " " + job.date.substr(8, 2) + ":" + job.date.substr(10, 2)
    }

    //--------------------------------------------------------------------
    // INITIALIZATION
    //--------------------------------------------------------------------
    var me = this;

  });
})();
