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
* - services.services.service-list
*
*/
(function(){
	var app = angular.module('services.services.service-list', []);

	app.factory("ServiceList", ['$rootScope', function($rootScope) {
		var services = [];
		var categories = [];
		var filters = [];
		var latest_versions = {};
		var categoryColors = ['yellow', 'green', 'red', 'blue', 'purple', 'pink', 'yellow2', 'green2', 'red2', 'blue2', 'purple2', 'pink2'];
		var iconColors = ["#2195C8", "#F5986D", "#07C680", "#F293AB", "#9C56DA", "#B6B406", "#D01D20", "#A86AC0", "#CAA301", "#98C9D8", "#5A7D9C", "#4C4646"];
		var old = new Date(0);
		//http://stackoverflow.com/questions/18247130/how-to-store-the-data-to-local-storage
		return {
			getServices: function() {
				return services;
			},
			setServices: function(_services) {
				services = this.adaptServicesInformation(_services);
				old = new Date();
				return this;
			},
			updateServices: function(newServices, soft) {
				var found, nElems = services.length;
				//For each new service check if it was already in the list
				for(var i in newServices){
					for(var j=0; j < nElems; j++){
						if(newServices[i].service === services[j].service){
							services[j].categories.replace(",updatable","");
							try{
								var _nv = Number.parseFloat(newServices[i].version.replace("v",""));
								var _cv = Number.parseFloat(services[j].version.replace("v",""));
								if(_nv > _cv){
									services[j].categories += ",updatable";
									services[j].update_candidates = (services[j].update_candidates || []);
									services[j].update_candidates.push({'title' : newServices[i].title + " v" + newServices[i].version, 'name':newServices[i].name});
								}
							}catch (e) {
								console.error("Error trying to compare the service versions.");
							}
						}
					}
					newServices[i].secondary_website = newServices[i].website;
					delete newServices[i].website;
					services.push(this.adaptServiceInformation(newServices[i]));
				}
				return this;
			},
			getService: function(service_id) {
				for(var i in services){
					if(services[i].id === service_id){
						return services[i];
					}
				}
				return null;
			},
			addService: function(service) {
				services.push(this.adaptServiceInformation(service));
				return this;
			},
			deleteService: function(service_id) {
				for(var i in services){
					if(services[i].id === service_id){
						services.splice(i,1);
						return services;
					}
				}
				return null;
			},
			adaptServicesInformation: function(services) {
				for(var i in services){
					this.adaptServiceInformation(services[i]);
				}
				return services;
			},
			adaptServiceInformation: function(service){
				if(service.installed !== undefined){
					service.categories += ",installed"
				}
				if(service.website !== undefined && service.website.indexOf("<HOST_NAME>") !== -1){
					service.website = service.website.replace("<HOST_NAME>", window.location.protocol + "//" + window.location.hostname);
				}

				// service.iconColor = colors[Math.floor(Math.random() * colors.length)];
				service.iconColor = this.getNextIconColor();
				return service;
			},
			getNextIconColor : function(){
				var color = iconColors.shift();
				iconColors.push(color);
				return color;
			},
			getCategories: function() {
				return categories;
			},
			getCategory: function(_category) {
				for(var i in categories){
					if(categories[i].name === _category){
						return categories[i];
					}
				}
				return null;
			},
			setCategories: function(_categories) {
				categories = _categories;
				return this;
			},
			updateCategories: function() {
				var categoriesAux = {}, _categories;

				for(var i in services){
					_categories = services[i].categories.split(",");
					for(var j in _categories){
						categoriesAux[_categories[j]] = {
							name: _categories[j],
							times: ((categoriesAux[_categories[j]] === undefined)?1:categoriesAux[_categories[j]].times + 1)
						}
					}
				}
				categories = Object.keys(categoriesAux).map(function(k) { return categoriesAux[k] });

				for(var i in categories){
					categories[i].color =  categoryColors[i%categoryColors.length]
				}

				return this;
			},
			getFilters: function() {
				return filters;
			},
			setFilters: function(_filters) {
				filters = _filters;
				return this;
			},
			removeFilter: function(_filter){
				var pos = filters.indexOf(_filter);
				if(pos !== -1){
					filters.splice(pos,1);
				}
				return this;
			},
			getOld: function(){
				return (new Date() - old)/120000;
			}
		};
	}]);
})();
