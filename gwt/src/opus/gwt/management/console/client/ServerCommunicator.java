/*############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
############################################################################*/

package opus.gwt.management.console.client;

import opus.gwt.management.console.client.dashboard.Dashboard;
import opus.gwt.management.console.client.deployer.AddAppsBuildProject;
import opus.gwt.management.console.client.deployer.AppBrowser;
import opus.gwt.management.console.client.deployer.AppIcon;
import opus.gwt.management.console.client.deployer.DatabaseOptions;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.Window;

public class ServerCommunicator {
	
	private int requestId;
	private Object[] queue;
	private String[] queryTypes;
	private ServerCommunicator serverComm;
	
	public ServerCommunicator() {
		this.queue = new Object[50];
		this.queryTypes = new String[50];
		this.requestId = 0;
		this.serverComm = this;
	}
	  /**
	   * Make call to remote server.
	   */
	
	public void getJson(String url, ServerCommunicator handler, String queryType, Object parent){
		//Window.alert(url + "     ---    " + String.valueOf(requestId));
		queue[requestId] = parent;
		queryTypes[requestId] = queryType;
		requestJson(requestId, url, serverComm);
		requestId++;
	}
	
	  public native static void requestJson(int requestId, String url,
	      ServerCommunicator handler) /*-{
	   var callback = "callback" + requestId;
		//alert(url+callback)
	   // [1] Create a script element.
	   var script = document.createElement("script");
	   script.setAttribute("src", url+callback);
	   script.setAttribute("type", "text/javascript");
		
	   // [2] Define the callback function on the window object.
	   window[callback] = function(jsonObj) {
	   // [3]		
	     handler.@opus.gwt.management.console.client.ServerCommunicator::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;Ljava/lang/String;I)(jsonObj, "null", requestId);

	     window[callback + "done"] = true;
	   }

	   // [4] JSON download has 1-second timeout.
	   setTimeout(function() {
	     if (!window[callback + "done"]) {
	       handler.@opus.gwt.management.console.client.ServerCommunicator::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;Ljava/lang/String;I)(null, "timeout", requestId);
	     }
	     // [5] Cleanup. Remove script and callback elements.
	     document.body.removeChild(script);
	     delete window[callback];
	     delete window[callback + "done"];
	   }, 10000);
	   
	   // [6] Attach the script element to the document body.
	   document.body.appendChild(script);
	  }-*/;
	  
	  /**
	   * Handle the response to the request for stock data from a remote server.
	   */
	public void handleJsonResponse(JavaScriptObject jso, String error, int rId) {
		String queryType = queryTypes[rId];

		if (jso == null) {
			if( error.equals("timeout") ) {
				Window.alert("JSON request timed out for request #" + String.valueOf(rId) + " = " + queryType);
				return;
			} else {
				Window.alert("no json returned for request # " + String.valueOf(rId) + " = " + queryType);
				return;	
			}
	    } else {
		    
		    Object parent = queue[rId];
		    
		    if (queryType.equals("updateTable")) {
		    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
		    	p.updateTable(p.asArrayOfAppData(jso));
		    } else if (queryType.equals("updateFieldList")) {
		    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
		    	p.updateFieldList(p.asModelProperties(jso));
		    } else if (queryType.equals("handleVersions")) {
		    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
		    	p.handleVersions(p.asArrayOfVersionData(jso));
		    } else if (queryType.equals("handleProjectNames")) {
		    	ManagementConsole mc = (ManagementConsole)parent;
		    	mc.handleProjectNames(mc.asArrayOfProjectNames(jso));
		    } else if (queryType.equals("handleProjectInformation")) {
		    	Dashboard db = (Dashboard)parent;
		    	db.handleProjectInformation(db.asJSOProjectInformation(jso));
		    } else if (queryType.equals("handleUserInformation")) {
		    	ManagementConsole mc = (ManagementConsole)parent;
		    	mc.handleUserInformation(mc.asJSOUserInformation(jso));
		    } else if (queryType.equals("importAppList")) {	    	
		    	AppBrowser p = (AppBrowser)parent;
		    	p.importAppList(p.asArrayOfProjectData(jso));
		    } else if (queryType.equals("handleDBOptions")){
		    	DatabaseOptions db = (DatabaseOptions)parent;
		    	db.handleDBOptions(db.asArrayOfDBOptionsData(jso));
		    } else if (queryType == "getAppInfo") {
		    	AppBrowser p = (AppBrowser)parent;
		    	p.populateAppGrid(p.asArrayOfAppData(jso));
		    } else if(queryType == "getVersionInfo"){
		    	AppIcon p = (AppIcon)parent;
		    	p.handleVersionInfo(p.asArrayOfVersionData(jso));
		    } else if(queryType == "getFeaturedList"){
		    	AppBrowser p = (AppBrowser)parent;
		    	p.populateFeaturedList(jso);
		    }
	    }
	  }
}
