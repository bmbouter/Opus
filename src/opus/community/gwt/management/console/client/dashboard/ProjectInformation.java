package opus.community.gwt.management.console.client.dashboard;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArrayString;

public class ProjectInformation extends JavaScriptObject {

	protected ProjectInformation(){}
	
	public final native JsArrayString getApps() /*-{ return this.apps; }-*/;
	public final native JsArrayString getURLS() /*-{ return this.urls; }-*/;
	public final native boolean getActive() /*-{ return this.active; }-*/;
	public final native String getDBName()  /*-{ return this.dbname; }-*/;
	public final native String getDBEngine()  /*-{ return this.dbengine; }-*/;
}
