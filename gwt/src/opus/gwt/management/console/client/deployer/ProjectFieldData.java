package opus.gwt.management.console.client.deployer;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;

public class ProjectFieldData extends JavaScriptObject { 
	protected ProjectFieldData() {}
	
	//public final native ProjectManualApplication getManualApps() /*-{ return this.manual_applications }-*/;
	public final native JsArray<ProjectCommunityApplication> getAsArrayOfCommunityApps() /*-{
		return this.versions 
	}-*/;
	
	public final native JsArray<ProjectManualApplication> getAsArrayOfManualApps() /*-{
		return this.manual_applications
	}-*/;
	
}
