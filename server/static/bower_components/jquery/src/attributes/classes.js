define(["../core","../core/stripAndCollapse","../var/rnothtmlwhite","../data/var/dataPriv","../core/init"],function(jQuery,stripAndCollapse,rnothtmlwhite,dataPriv){"use strict";function getClass(elem){return elem.getAttribute&&elem.getAttribute("class")||""}jQuery.fn.extend({addClass:function(value){var classes,elem,cur,curValue,clazz,j,finalValue,i=0;if(jQuery.isFunction(value)){return this.each(function(j){jQuery(this).addClass(value.call(this,j,getClass(this)))})}if(typeof value==="string"&&value){classes=value.match(rnothtmlwhite)||[];while(elem=this[i++]){curValue=getClass(elem);cur=elem.nodeType===1&&" "+stripAndCollapse(curValue)+" ";if(cur){j=0;while(clazz=classes[j++]){if(cur.indexOf(" "+clazz+" ")<0){cur+=clazz+" "}}finalValue=stripAndCollapse(cur);if(curValue!==finalValue){elem.setAttribute("class",finalValue)}}}}return this},removeClass:function(value){var classes,elem,cur,curValue,clazz,j,finalValue,i=0;if(jQuery.isFunction(value)){return this.each(function(j){jQuery(this).removeClass(value.call(this,j,getClass(this)))})}if(!arguments.length){return this.attr("class","")}if(typeof value==="string"&&value){classes=value.match(rnothtmlwhite)||[];while(elem=this[i++]){curValue=getClass(elem);cur=elem.nodeType===1&&" "+stripAndCollapse(curValue)+" ";if(cur){j=0;while(clazz=classes[j++]){while(cur.indexOf(" "+clazz+" ")>-1){cur=cur.replace(" "+clazz+" "," ")}}finalValue=stripAndCollapse(cur);if(curValue!==finalValue){elem.setAttribute("class",finalValue)}}}}return this},toggleClass:function(value,stateVal){var type=typeof value;if(typeof stateVal==="boolean"&&type==="string"){return stateVal?this.addClass(value):this.removeClass(value)}if(jQuery.isFunction(value)){return this.each(function(i){jQuery(this).toggleClass(value.call(this,i,getClass(this),stateVal),stateVal)})}return this.each(function(){var className,i,self,classNames;if(type==="string"){i=0;self=jQuery(this);classNames=value.match(rnothtmlwhite)||[];while(className=classNames[i++]){if(self.hasClass(className)){self.removeClass(className)}else{self.addClass(className)}}}else if(value===undefined||type==="boolean"){className=getClass(this);if(className){dataPriv.set(this,"__className__",className)}if(this.setAttribute){this.setAttribute("class",className||value===false?"":dataPriv.get(this,"__className__")||"")}}})},hasClass:function(selector){var className,elem,i=0;className=" "+selector+" ";while(elem=this[i++]){if(elem.nodeType===1&&(" "+stripAndCollapse(getClass(elem))+" ").indexOf(className)>-1){return true}}return false}})});