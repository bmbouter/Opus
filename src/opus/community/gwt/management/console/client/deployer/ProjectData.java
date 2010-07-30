package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;

class ProjectData extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected ProjectData() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native ProjectFieldData getFields() /*-{ return this.fields; }-*/; // [3]
  public final native String getName() /*-{ return this.name }-*/;
  
}