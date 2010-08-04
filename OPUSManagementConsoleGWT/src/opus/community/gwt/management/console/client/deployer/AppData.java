package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;

class AppData extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected AppData() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native String getName() /*-{ return this.pk; }-*/; // [3]
  public final native String getContact() /*-{ return this.fields.contact; }-*/;
  public final native String getDescription() /*-{ return this.fields.description; }-*/; 
  public final native String getModel() /*-{ return this.model; }-*/; 
} 
