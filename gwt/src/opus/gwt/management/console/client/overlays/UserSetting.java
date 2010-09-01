package opus.gwt.management.console.client.overlays;
import com.google.gwt.core.client.JavaScriptObject;

public class UserSetting extends JavaScriptObject{
	protected UserSetting() {}
	
	public final native JavaScriptObject getSetting() /*-{ return this }-*/;

}
