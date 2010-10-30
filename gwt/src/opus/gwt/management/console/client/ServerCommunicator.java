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

import java.util.HashMap;

import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.AsyncRequestEventHandler;
import opus.gwt.management.console.client.event.GetApplicationsEvent;
import opus.gwt.management.console.client.event.GetProjectsEvent;
import opus.gwt.management.console.client.event.ImportAppListEvent;
import opus.gwt.management.console.client.event.UpdateApplicationEvent;
import opus.gwt.management.console.client.event.UpdateDBOptionsEvent;
import opus.gwt.management.console.client.event.UpdateFeaturedListEvent;
import opus.gwt.management.console.client.event.UpdateProjectsEvent;
import opus.gwt.management.console.client.event.UpdateVersionEvent;
import opus.gwt.management.console.client.event.GetUserEvent;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.http.client.URL;

public class ServerCommunicator {
	
	private final String userURL = "/json/username/?a&callback=";
	private final String dbOptionsURL = "/json/database/?callback=";
	private final String applicationURL = "/json/search/application/?a&callback=";
	private final String featuredListURL =  "/json/featured/?a&callback=";
	private final String importAppListURL = "/project/configuration/<placeHolder>/?callback=";
	private final String versionURL = "/json/application/<placeHolder>/versions/?a&callback=";
	private final String projectURL = "/json/projects/<placeHolder>/?a&callback=";
	
	private int requestId;
	private HashMap<Integer, String> queryTypes;
	private EventBus eventBus;
	private JSVariableHandler JSvarHandler;
	private HashMap<String, String> URLS;
	private ClientFactory clientFactory;
	
	public ServerCommunicator(ClientFactory clientFactory) {
		this.URLS = new HashMap<String, String>();
		this.queryTypes = new HashMap<Integer, String>();
		this.requestId = 0;
		this.clientFactory = clientFactory;
		this.eventBus = clientFactory.getEventBus();
		JSvarHandler = clientFactory.getJSVariableHandler();
		setupURLS();
		registerHandlers();
	}
	
	private void setupURLS(){
		URLS.put("getUser", JSvarHandler.getDeployerBaseURL() + userURL);
		URLS.put("handleDBOptions", JSvarHandler.getDeployerBaseURL() + dbOptionsURL);
		URLS.put("handleApplication", JSvarHandler.getRepoBaseURL() + applicationURL);
		URLS.put("handleFeaturedList", JSvarHandler.getRepoBaseURL() + featuredListURL);
		URLS.put("handleImportAppList", JSvarHandler.getRepoBaseURL() + importAppListURL);
		URLS.put("handleVersion", JSvarHandler.getRepoBaseURL() + versionURL);
		URLS.put("updateProjects", JSvarHandler.getDeployerBaseURL() + projectURL);
		URLS.put("getProjects", JSvarHandler.getDeployerBaseURL() + projectURL);
		URLS.put("getApplications", JSvarHandler.getRepoBaseURL() + applicationURL);
	}
	
	private void registerHandlers(){
		eventBus.addHandler(AsyncRequestEvent.TYPE, 
			new AsyncRequestEventHandler(){
				public void onAsyncRequest(AsyncRequestEvent event){
					if( event.hasUrlVariable() ){
						getJson(URL.encode(URLS.get(event.getRequestHandle()).replaceAll("<placeHolder>", event.getUrlVariable())), event.getRequestHandle());
					} else {
						getJson(URL.encode(URLS.get(event.getRequestHandle())), event.getRequestHandle());
					}
				}
		});
	}

	public void getJson(String url, String queryType){
		queryTypes.put(requestId, queryType);
		requestJson(requestId, url, this);
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
	
	public void handleJsonResponse(JavaScriptObject jso, String error, int rId) {
		String queryType = queryTypes.remove(rId);
		
		if (jso == null) {
			if( error.equals("timeout") ) {
				//Window.alert("JSON request timed out for request #" + String.valueOf(rId) + " = " + queryType);
				return;
			} else {
				//Window.alert("no json returned for request # " + String.valueOf(rId) + " = " + queryType);
				return;	
			}
	    } else {
	    	
		    if (queryType.equals("getUser")) {
		    	eventBus.fireEvent(new GetUserEvent(jso));
		    } else if (queryType == "handleApplication") {
		    	eventBus.fireEvent(new UpdateApplicationEvent(jso));
		    } else if(queryType == "handleFeaturedList"){
		    	eventBus.fireEvent(new UpdateFeaturedListEvent(jso));
		    } else if (queryType.equals("handleDBOptions")){
		    	eventBus.fireEvent(new UpdateDBOptionsEvent(jso));
		    } else if (queryType.equals("updateProjects")) {
		     	eventBus.fireEvent(new UpdateProjectsEvent(jso, clientFactory));
		    } else if (queryType.equals("handleImportAppList")) {	
		    	eventBus.fireEvent(new ImportAppListEvent(jso));
		    } else if(queryType == "handleVersion") {
		    	eventBus.fireEvent(new UpdateVersionEvent(jso));
		    } else if(queryType.equals("getProjects")) {
		    	eventBus.fireEvent(new GetProjectsEvent(jso));
		    } else if(queryType.equals("getApplications")) {
		    	eventBus.fireEvent(new GetApplicationsEvent(jso));
		    }
	    }
	}
}
