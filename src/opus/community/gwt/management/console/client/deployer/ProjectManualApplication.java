package opus.community.gwt.management.console.client.deployer;
import com.google.gwt.core.client.JavaScriptObject;

public class ProjectManualApplication extends JavaScriptObject{
	protected ProjectManualApplication() {}
	
	public final native String getPath() /*-{ return this.path }-*/;
	public final native String getName() /*-{ return this.name }-*/;
	public final native String getType() /*-{ return this.type }-*/;
}
