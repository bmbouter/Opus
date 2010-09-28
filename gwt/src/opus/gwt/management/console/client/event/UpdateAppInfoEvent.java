package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.AppInfo;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateAppInfoEvent extends GwtEvent<UpdateAppInfoEventHandler> {
	
	public static Type<UpdateAppInfoEventHandler> TYPE = new Type<UpdateAppInfoEventHandler>();
	private JsArray<AppInfo> appInfo;
	
	public UpdateAppInfoEvent(JavaScriptObject appInfo){
		this.appInfo = ConvertAppInfo(appInfo);
	}
	
	public JsArray<AppInfo> getAppInfo(){
		return appInfo;
	}
	
  	@Override
  	public Type<UpdateAppInfoEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateAppInfoEventHandler handler) {
	  handler.onUpdateAppInfo(this);
  	}
  	
	public final native JsArray<AppInfo> ConvertAppInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}