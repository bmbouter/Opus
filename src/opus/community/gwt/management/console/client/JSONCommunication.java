package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.deployer.AddAppsBuildProject;

import com.google.gwt.core.client.JavaScriptObject;

public class JSONCommunication {
	
	private Object parent;
	private JavaScriptObject data;
	private String error;
	
	public JSONCommunication(Object parent) {
		this.parent = parent;
	}
	  /**
	   * Make call to remote server.
	   */
	  public native static void getJson(int requestId, String url,
	      JSONCommunication handler, int queryType) /*-{
	   
	   var callback = "callback" + requestId;
	   
	   // [1] Create a script element.
	   var script = document.createElement("script");
	   script.setAttribute("src", url+callback);
	   script.setAttribute("type", "text/javascript");

	   // [2] Define the callback function on the window object.
	   window[callback] = function(jsonObj) {
	   // [3]
	     handler.@opus.community.gwt.management.console.client.JSONCommunication::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;I)(jsonObj, queryType);
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
	   }, 1000);

	   // [6] Attach the script element to the document body.
	   document.body.appendChild(script);
	  }-*/;
	  
	  /**
	   * Handle the response to the request for stock data from a remote server.
	   */
	  public void handleJsonResponse(JavaScriptObject jso, int queryType) {

	    if (jso == null) {
	      this.error = "Error occured while retrieving JSON.";
	      return;
	    }
	    this.error = null;
	    //Window.alert(Integer.toString(queryType));
	    
	    if (queryType == 1) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.updateTable(p.asArrayOfAppData(jso));
	    } else if (queryType == 2) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.updateFieldList(p.asModelProperties(jso));
	    } else if (queryType == 3) {
	    	AddAppsBuildProject p = (AddAppsBuildProject)parent;
	    	p.handleVersions(p.asArrayOfVersionData(jso));
	    }
	    
	  }
	  
	  public JavaScriptObject getData(){
		  return data;
	  }
}
