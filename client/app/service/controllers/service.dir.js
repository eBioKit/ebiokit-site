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
*
*/
(function(){
	var app = angular.module('services.directives.service-directives', []);

	app.directive("mainMenu", function() {
		return {
			restrict: 'E',
			templateUrl: 'static/app/service/templates/main-menu.tpl.html'
		};
	});
})();
