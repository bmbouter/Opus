package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.Application;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateAppInfoEvent extends GwtEvent<UpdateAppInfoEventHandler> {
	
	public static Type<UpdateAppInfoEventHandler> TYPE = new Type<UpdateAppInfoEventHandler>();
	private JsArray<Application> application;
	
	public UpdateAppInfoEvent(JavaScriptObject appInfo){
		this.application = ConvertAppInfo(appInfo);
	}
	
	public JsArray<Application> getAppInfo(){
		return application;
	}
	
  	@Override
  	public Type<UpdateAppInfoEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateAppInfoEventHandler handler) {
	  handler.onUpdateAppInfo(this);
  	}
  	
	public final native JsArray<Application> ConvertAppInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}