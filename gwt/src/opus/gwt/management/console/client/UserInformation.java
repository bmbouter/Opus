package opus.gwt.management.console.client;

import com.google.gwt.core.client.JavaScriptObject;

class UserInformation extends JavaScriptObject {                              // [1]
	  // Overlay types always have protected, zero argument constructors.
	  protected UserInformation() {}

	  public final native String getUsername() /*-{ return this.username; }-*/;
	  public final native boolean isAuthenticated() /*-{ return this.authenticated; }-*/;  
}
