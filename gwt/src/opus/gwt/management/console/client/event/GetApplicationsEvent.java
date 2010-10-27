package opus.gwt.management.console.client.event;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.Application;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class GetApplicationsEvent extends GwtEvent<GetApplicationsEventHandler> {
	
	public static Type<GetApplicationsEventHandler> TYPE = new Type<GetApplicationsEventHandler>();
	private JsArray<Application> applicationsArray;
	private HashMap<String, Application> applicationsMap = new HashMap<String, Application>();
	
	public GetApplicationsEvent(JavaScriptObject applications){
		this.applicationsArray = ConvertAppInfo(applications);
		processApplications();
	}
	
	private void processApplications() {
		for(int i = 0; i < applicationsArray.length(); i++) {
			Application app = applicationsArray.get(i);
			applicationsMap.put(app.getAppName(), app);
		}
	}
	
	public HashMap<String, Application> getApplications(){
		return applicationsMap;
	}
	
  	@Override
  	public Type<GetApplicationsEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(GetApplicationsEventHandler handler) {
	  handler.onGetApplications(this);
  	}
  	
	public final native JsArray<Application> ConvertAppInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}