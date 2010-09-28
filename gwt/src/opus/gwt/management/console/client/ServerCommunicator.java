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
import opus.gwt.management.console.client.event.CheckAuthenticationEvent;
import opus.gwt.management.console.client.event.CheckAuthenticationEventHandler;
import opus.gwt.management.console.client.event.GetAppInfoEvent;
import opus.gwt.management.console.client.event.GetAppInfoEventHandler;
import opus.gwt.management.console.client.event.UpdateAppInfoEvent;
import opus.gwt.management.console.client.event.UpdateAppInfoEventHandler;
import opus.gwt.management.console.client.event.UserInfoEvent;
import opus.gwt.management.console.client.overlays.AppInfo;
import opus.gwt.management.console.client.overlays.DatabaseOptionsData;
import opus.gwt.management.console.client.overlays.ModelProperties;
import opus.gwt.management.console.client.overlays.ProjectCommunityApplication;
import opus.gwt.management.console.client.overlays.ProjectData;
import opus.gwt.management.console.client.overlays.ProjectFieldData;
import opus.gwt.management.console.client.overlays.ProjectInformation;
import opus.gwt.management.console.client.overlays.ProjectManualApplication;
import opus.gwt.management.console.client.overlays.ProjectNames;
import opus.gwt.management.console.client.overlays.UserInformation;
import opus.gwt.management.console.client.overlays.VersionData;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.Window;

public class ServerCommunicator {
	
	private final String checkLoginURL = "/json/username/?a&callback=";
	private final String appListURL = "/json/search/application/?a&callback=";
	
	private int requestId;
	private Object[] queue;
	private String[] queryTypes;
	private HandlerManager eventBus;
	private ServerCommunicator handler;
	private JSVariableHandler JSvarHandler;
	
	public ServerCommunicator(HandlerManager eventBus) {
		this.queue = new Object[50];
		this.queryTypes = new String[50];
		this.requestId = 0;
		this.eventBus = eventBus;
		this.handler = this;
		JSvarHandler = new JSVariableHandler();
		registerEvents();
	}

	public void getJson(String url, String queryType, Object parent){
		queue[requestId] = parent;
		queryTypes[requestId] = queryType;
		requestJson(requestId, url, handler);
		requestId++;
	}
	
	public native static void requestJson(int requestId, String url, ServerCommunicator handler) /*-{
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
		    
		    if (queryType.equals("handleUserInformation")) {
		    	eventBus.fireEvent(new UserInfoEvent(jso));
		    } else if (queryType == "handleAppInfo") {
		    	eventBus.fireEvent(new UpdateAppInfoEvent(jso));
		    } else if (queryType.equals("updateFieldList")) {
		    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
		    	p.updateFieldList(asModelProperties(jso));
		    } else if (queryType.equals("handleVersions")) {
		    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
		    	p.handleVersions(asArrayOfVersionData(jso));
		    } else if (queryType.equals("handleProjectInformation")) {
		    	Dashboard db = (Dashboard)parent;
		    	db.handleProjectInformation(asJSOProjectInformation(jso));
		    } else if (queryType.equals("importAppList")) {	    	
		    	AppBrowser p = (AppBrowser)parent;
		    	p.importAppList(asArrayOfProjectData(jso));
		    } else if (queryType.equals("handleDBOptions")){
		    	DatabaseOptions db = (DatabaseOptions)parent;
		    	db.handleDBOptions(asArrayOfDBOptionsData(jso));
		    } else if(queryType == "getVersionInfo"){
		    	AppIcon p = (AppIcon)parent;
		    	p.handleVersionInfo(asArrayOfVersionData(jso));
		    } else if(queryType == "getFeaturedList"){
		    	AppBrowser p = (AppBrowser)parent;
		    	p.populateFeaturedList(jso);
		    }
	    }
	  }
	
	private void registerEvents(){
		eventBus.addHandler(CheckAuthenticationEvent.TYPE, 
			new CheckAuthenticationEventHandler(){
				public void onCheckAuthentication(CheckAuthenticationEvent event){
					getJson(URL.encode(JSvarHandler.getDeployerBaseURL() + checkLoginURL), "handleUserInformation", (Object)this);
				}
		});
		eventBus.addHandler(GetAppInfoEvent.TYPE, 
			new GetAppInfoEventHandler(){
				public void onGetAppInfo(GetAppInfoEvent event){
					getJson(URL.encode(JSvarHandler.getRepoBaseURL() + appListURL), "handleAppInfo", (Object)this);
				}
		});
	}
	
	public final native DatabaseOptionsData asArrayOfDBOptionsData(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
	
	public final native JsArray<ProjectNames> asArrayOfProjectNames(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
	  
	  public final native ModelProperties asModelProperties(JavaScriptObject jso) /*-{
	    return jso;
	  }-*/;
	  
	  public final native JsArray<VersionData> asArrayOfVersionData(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;
	  
	  public final native JsArray<ProjectData> asArrayOfProjectData(JavaScriptObject jso) /*-{
		return jso;
	  }-*/;
	  
	  public final native JsArray<ProjectFieldData> asArrayOfProjectFieldData(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;
	  
	  public final native JsArray<ProjectManualApplication> asArrayOfProjectManualApplications(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;	
	  
	  public final native JsArray<ProjectCommunityApplication> asArrayOfProjectCommunityApplications(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;

	public final native ProjectInformation asJSOProjectInformation(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}
