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
* - jobs.services.job-list
*
*/
(function(){
	var app = angular.module('jobs.services.job-list', []);

	app.factory("JobList", ['$rootScope', function($rootScope) {
		var jobs = [];
		var old = new Date(0);
		//http://stackoverflow.com/questions/18247130/how-to-store-the-data-to-local-storage
		return {
			getJobs: function() {
				return jobs;
			},
			setJobs: function(_jobs) {
				jobs = this.adaptJobsInformation(_jobs);
				old = new Date();
				return this;
			},
			getJob: function(job_id) {
				for(var i in jobs){
					if(jobs[i].id === job_id){
						return jobs[i];
					}
				}
				return null;
			},
			addJob: function(job) {
				jobs.push(this.adaptJobInformation(job));
				return this;
			},
			deleteJob: function(job_id) {
				for(var i in jobs){
					if(jobs[i].id === job_id){
						jobs.splice(i,1);
						return jobs;
					}
				}
				return null;
			},
			adaptJobsInformation: function(jobs) {
				for(var i in jobs){
					this.adaptJobInformation(jobs[i]);
				}
				return jobs;
			},
			adaptJobInformation: function(job){
				var erroneous = 0, finished = 0, waiting=0;
				for(i in job.tasks){
					if(job.tasks[i].status === "FAILED" || job.tasks[i].status === "NOT_QUEUED"){
						erroneous++;
					}else if(job.tasks[i].status === "FINISHED"){
						finished++;
					}else if(job.tasks[i].status === "QUEUED"){
						waiting++;
					}
				}
				job.progress = Math.round(finished/job.tasks.length*100);
				if(finished === job.tasks.length){
					job.status = "Done";
				}else if(erroneous > 0){
					job.status = "Failed";
				}else if(waiting === job.tasks.length){
					job.status = "Waiting";
				}else{
					job.status = "Running";
				}
				return job;
			},
			getOld: function(){
				return (new Date() - old)/120000;
			}
		};
	}]);
})();
