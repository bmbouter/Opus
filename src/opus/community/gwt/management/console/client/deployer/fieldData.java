package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;

class fieldData extends JavaScriptObject {                              // [1]
	  // Overlay types always have protected, zero argument constructors.
	  protected fieldData() {}                                              // [2]

	  // JSNI methods to get stock data.
	  public final native String toStr() /*-{ return this[0]; }-*/; // [3]
	 
	} 