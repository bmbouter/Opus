package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.AppInfo;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class GetAppInfoEvent extends GwtEvent<GetAppInfoEventHandler> {
	
	public static Type<GetAppInfoEventHandler> TYPE = new Type<GetAppInfoEventHandler>();
	private JsArray<AppInfo> appInfo;
	
  	@Override
  	public Type<GetAppInfoEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(GetAppInfoEventHandler handler) {
	  handler.onGetAppInfo(this);
  	}
  	
	public final native JsArray<AppInfo> ConvertAppInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}
