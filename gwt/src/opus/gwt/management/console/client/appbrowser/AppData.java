package opus.gwt.management.console.client.appbrowser;

import com.google.gwt.core.client.JavaScriptObject;

class AppData extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected AppData() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native int getPk() /*-{ return this.pk }-*/;
  public final native String getName() /*-{ return this.fields.name; }-*/; // [3]
  public final native String getContact() /*-{ return this.fields.contact; }-*/;
  public final native String getDescription() /*-{ return this.fields.description; }-*/; 
  public final native String getModel() /*-{ return this.model; }-*/; 
  public final native String getIconURL() /*-{
		var url = this.fields.icon_url;
		if( url == "" ){
			return null;
		} else if( url == null ){
			return null;
		} else if( url == undefined ){
			return null;
		} else {
			return ''+url;
		} 
	}-*/; 
  public final native String getPath() /*-{ return this.fields.path; }-*/;
} 
