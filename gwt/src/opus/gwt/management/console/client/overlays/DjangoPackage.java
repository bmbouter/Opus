package opus.gwt.management.console.client.overlays;

import com.google.gwt.core.client.JavaScriptObject;

public class DjangoPackage extends JavaScriptObject {
	protected DjangoPackage(){}
	
	public final native int getPk() /*-{ return this.pk }-*/;
	public final native String getDescription() /*-{ return this.fields.description; }-*/; 
	public final native String getPath()  /*-{ return this.fields.path; }-*/;
	public final native String getType()  /*-{ return this.fields.type; }-*/;
	public final native String getAppName()  /*-{ return this.fields.app_name; }-*/;
	public final native String getDPId()  /*-{ return this.fields.dp_id; }-*/;
}
