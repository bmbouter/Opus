package opus.community.gwt.management.console.client;

import com.google.gwt.core.client.JavaScriptObject;

	
class ProjectNames extends JavaScriptObject {                              // [1]
	  // Overlay types always have protected, zero argument constructors.
	  protected ProjectNames() {}

	  public final native String getName() /*-{ return this.name; }-*/;  
} 
