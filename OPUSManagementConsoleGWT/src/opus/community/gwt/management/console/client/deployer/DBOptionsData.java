package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;

public class DBOptionsData extends JavaScriptObject {
	protected DBOptionsData() {}                                 

	public final native JavaScriptObject getDBOptions() /*-{ return this.options; }-*/;
	 
}
