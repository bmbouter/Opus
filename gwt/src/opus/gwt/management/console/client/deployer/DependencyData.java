package opus.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;

class DependencyData extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected DependencyData() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native String getName() /*-{ return this.name; }-*/; // [3]
  public final native String getVersion() /*-{ return this.version_number; }-*/;

}
