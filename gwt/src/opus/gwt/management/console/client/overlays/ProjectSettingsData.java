package opus.gwt.management.console.client.overlays;
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
		
		for(var i=0; i<settings.length; i++) {
			if (settings[i][2] == "choice") {
				//alert(settings[i][3][2]);
			}
		}
		return settings;
	}-*/;

	public final native JsArray<JavaScriptObject> getSettingsArray(JavaScriptObject setting) /*-{
//		alert("Setting: " + setting);
//		if(setting[2] == "choice") {
//			var options = "";
//			var selected = "";
//			
//			for(var i=0; i<setting[3][0].length-1; i++) {
//				if (setting[3][i][2] == "true"){
//					selected = "selected='selected'";
//				}
//				options += "<option value='" +setting[3][i][0] + "'" + selected + ">" + setting[3][i][1] + "</option>\n";
//			}
//			setting[3] = options;
//		}
		return setting;
	}-*/;
	
	public final native String getChoiceSettingsArray(JavaScriptObject setting) /*-{
		
		if(setting[2] == "choice") {
			var options = "";
			var selected = "";
			var choiceSettings = setting[3];
			
			for(var i = 0; i < choiceSettings[0].length - 1; i++) {
				if(choiceSettings[i][2] == "true")
					selected = "selected='selected'";
				
				options = "<option value='" + choiceSettings[i][0] + "'" + selected + ">" + choiceSettings[i][1] + "</option>\n";
			}
			
			choiceSettings = options;
			
			return choiceSettings;
		}
		
		return "";
	}-*/;
	
	public final native JavaScriptObject getNext() /*-{
		return current;
	}-*/;
	
	public final native JsArray<JavaScriptObject> getChoices(String choices) /*-{
		return choices;
	}-*/;
	
	public final native int getNumberOfApplications() /*-{
		var size = 0;
		for (app in app.settings) {
			size++;
		}
		return size;
	}-*/;
}
