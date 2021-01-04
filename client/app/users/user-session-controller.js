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
 * - UserSessionController
 *
 */
(function() {
    var app = angular.module('users.controllers.user-session', [
        'ang-dialogs',
        'ui.router',
    ]);

    app.controller('UserSessionController', function($state, $rootScope, $scope, $http, $dialogs, $cookies, APP_EVENTS) {
        //--------------------------------------------------------------------
        // CONTROLLER FUNCTIONS
        //--------------------------------------------------------------------

        //--------------------------------------------------------------------
        // EVENT HANDLERS
        //--------------------------------------------------------------------
        this.signFormSubmitHandler = function() {
            if ($scope.isLogin) {
                this.signInButtonHandler();
            } else {
                this.signUpButtonHandler();
            }
        };

        this.signInButtonHandler = function() {
            if ($scope.userInfo.email !== '' && $scope.userInfo.password !== '') {
                $http($rootScope.getHttpRequestConfig("POST", "session-rest", {
                    data: {
                        "token": btoa($scope.userInfo.email + ":" + $scope.userInfo.password)
                    }
                })).then(
                    function successCallback(response) {
                        response = response.data;
                        if(response.success){
                            //CLEAN PREVIOUS COOKIES
                            $cookies.remove("ebiokitsession", {
                                path: getPathname()
                            });
                            //SET THE COOKIES
                            $cookies.put("ebiokitsession", btoa($scope.userInfo.email + ":" + response.session_token));
                            $scope.userInfo.email = $scope.userInfo.email;
                            delete $scope.userInfo.password
                            delete $scope.signForm
                            //Notify all the other controllers that user has signed in
                            $rootScope.$broadcast(APP_EVENTS.loginSuccess);
                            $state.go('control-panel');
                        } else {
                            $scope.errorMessage = response.other.error_message
                            return;
                        }
                    },
                    function errorCallback(response) {
                        debugger;
                        var message = "Failed during sign-in process.";
                        $dialogs.showErrorDialog(message, {
                            logMessage: message + " at UserSessionController:signInButtonHandler."
                        });
                        console.error(response.data);
                    }
                );
            };
        };

        this.signUpButtonHandler = function() {
            valid = $scope.userInfo.email !== ''
            valid &= $scope.userInfo.username !== ''
            valid &= $scope.userInfo.password.length > 7
            valid &= $scope.userInfo.password === $scope.userInfo.passconfirm
            if ( valid ) {
                $http($rootScope.getHttpRequestConfig("POST", "user-rest", {
                    data: $scope.userInfo
                })).then(
                    function successCallback(response) {
                        response = response.data;
                        if (response.success === true) {
                            $dialogs.showSuccessDialog("User account succesfully created.");
                            $scope.isLogin = true;
                        } else {
                            $scope.errorMessage = response.other.error_message
                            return;
                        }
                    },
                    function errorCallback(response) {
                        if (response.data && [404001].indexOf(response.data.err_code) !== -1) {
                            $dialogs.showErrorDialog("Invalid user or password.");
                            return;
                        }
                        debugger;
                        var message = "Failed during sign-up process.";
                        $dialogs.showErrorDialog(message, {
                            logMessage: message + " at UserSessionController:signUpButtonHandler."
                        });
                        console.error(response.data);
                    }
                );
            } else if($scope.userInfo.password === ""){
                $scope.errorMessage = "Password can not be empty."
            } else if($scope.userInfo.password !== $scope.userInfo.passconfirm){
                $scope.errorMessage = "Passwords do not match."
            } else if($scope.userInfo.password.length <= 7){
                $scope.errorMessage = "Password must contain at least 8 characters (one upper case, one number and no spaces)."
            };
        };

        this.signOutButtonHandler = function() {
            delete $scope.userInfo.email;

            $http($rootScope.getHttpRequestConfig("DELETE", "session-rest", {
                data: {
                    "token": btoa($scope.userInfo.email + ":" + $scope.userInfo.password)
                }
            })).then(
                function successCallback(response) {
                    $cookies.remove("ebiokitsession", {
                        path: getPathname()
                    });
                    $state.go('signin');
                    window.location.reload()
                },
                function errorCallback(response) {
                    $cookies.remove("ebiokitsession", {
                        path: getPathname()
                    });
                    $state.go('signin');
                    window.location.reload()

                    var message = "Failed during sign-out process.";
                    $dialogs.showErrorDialog(message, {
                        logMessage: message + " at UserSessionController:signOutButtonHandler."
                    });
                    console.error(response.data);
                }
            );

            //Notify all the other controllers that user has signed in
            $rootScope.$broadcast(APP_EVENTS.logoutSuccess);
        };

        //--------------------------------------------------------------------
        // INITIALIZATION
        //--------------------------------------------------------------------
        $scope.userInfo = {
            email: ""
        };
    });
})();
