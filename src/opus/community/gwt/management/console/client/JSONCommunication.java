package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.deployer.AddAppsBuildProject;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.Window;

public class JSONCommunication {
	
	private JavaScriptObject data;
	private String error;
	private int requestId;
	private Object[] queue;
	private int[] queryTypes;
	
	public JSONCommunication() {
		this.queue = new Object[20];
		this.queryTypes = new int[20];
		this.requestId = 0;
	}
	  /**
	   * Make call to remote server.
	   */
	
	public void getJson(String url, JSONCommunication handler, int queryType, Object parent){
		//Window.alert(String.valueOf(queryType));
		queue[requestId] = parent;
		queryTypes[requestId] = queryType;
		requestJson(requestId, url, handler, queryType);
		requestId++;
	}
	
	  public native static void requestJson(int requestId, String url,
	      JSONCommunication handler, int queryType) /*-{
	   var callback = "callback" + requestId;

	   // [1] Create a script element.
	   var script = document.createElement("script");
	   script.setAttribute("src", url+callback);
	   script.setAttribute("type", "text/javascript");
		
	   // [2] Define the callback function on the window object.
	   window[callback] = function(jsonObj) {
	   // [3]		
	     handler.@opus.community.gwt.management.console.client.JSONCommunication::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;I)(jsonObj, requestId);

	     window[callback + "done"] = true;
	   }

	   // [4] JSON download has 1-second timeout.
	   setTimeout(function() {
	     if (!window[callback + "done"]) {
	       handler.@opus.community.gwt.management.console.client.JSONCommunication::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;I)(null);
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
	  public void handleJsonResponse(JavaScriptObject jso, int rId) {
	    int queryType = queryTypes[rId];
	    //Window.alert(String.valueOf(queryType));

		if (jso == null) {
			Window.alert("no json returned");
			this.error = "Error occured while retrieving JSON.";
	      return;
	    }
		
	    this.error = null;
	    Object parent = queue[rId];
	    
	    if (queryType == 1) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.updateTable(p.asArrayOfAppData(jso));
	    } else if (queryType == 2) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.updateFieldList(p.asModelProperties(jso));
	    } else if (queryType == 3) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.handleVersions(p.asArrayOfVersionData(jso));
	    } else if (queryType == 4) {
	    	ManagementConsole mc = (ManagementConsole)parent;
	    	mc.handleProjectNames(mc.asArrayOfProjectNames(jso));
	    }
	    
	  }
	  
	  public JavaScriptObject getData(){
		  return data;
	  }
}
