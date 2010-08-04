package opus.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;


class ModelProperties extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected ModelProperties() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native JavaScriptObject getFields() /*-{ return this.fields; }-*/; // [3]
 
} 
