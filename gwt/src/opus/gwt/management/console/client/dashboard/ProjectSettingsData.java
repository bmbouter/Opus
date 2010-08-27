package opus.gwt.management.console.client.dashboard;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;

public class ProjectSettingsData extends JavaScriptObject{
	
	protected ProjectSettingsData() {}
	
	public final native String getApplicationSettings() /*-{ 
		var apps = new Array();
		for (app in this) {
			apps.push(app);
		}
		return apps.join(";;;");
	}-*/;
	
	public final native JsArray<JavaScriptObject> getAppSettings(String appname) /*-{
		var settings = this[appname];
		return settings;
	}-*/;

	public final native JsArray<JavaScriptObject> getSettingsArray(JavaScriptObject setting) /*-{
		return setting;
	}-*/;
	
	public final native JavaScriptObject getNext() /*-{
		return current;
	}-*/;
	
	public final native int getNumberOfApplications() /*-{
		var size = 0;
		for (app in app.settings) {
			size++;
		}
		return size;
	}-*/;
}
