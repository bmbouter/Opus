package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.VersionData;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateVersionInfoEvent extends GwtEvent<UpdateVersionInfoEventHandler> {
	
	public static Type<UpdateVersionInfoEventHandler> TYPE = new Type<UpdateVersionInfoEventHandler>();
	private JsArray<VersionData> versionInfo;
	
	public UpdateVersionInfoEvent(JavaScriptObject jso){
		this.versionInfo = ConvertVersionInfo(jso);
	}
	
	public JsArray<VersionData> getVersionInfo(){
		return versionInfo;
	}
	
  	@Override
  	public Type<UpdateVersionInfoEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateVersionInfoEventHandler handler) {
	  handler.onUpdateVersionInfo(this);
  	}
  	
	public final native JsArray<VersionData> ConvertVersionInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}