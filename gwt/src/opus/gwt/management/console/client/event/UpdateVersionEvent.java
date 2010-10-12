package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.VersionData;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateVersionEvent extends GwtEvent<UpdateVersionEventHandler> {
	
	public static Type<UpdateVersionEventHandler> TYPE = new Type<UpdateVersionEventHandler>();
	private JsArray<VersionData> versionInfo;
	
	public UpdateVersionEvent(JavaScriptObject jso){
		this.versionInfo = ConvertVersionInfo(jso);
	}
	
	public JsArray<VersionData> getVersionInfo(){
		return versionInfo;
	}
	
  	@Override
  	public Type<UpdateVersionEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateVersionEventHandler handler) {
	  handler.onUpdateVersionInfo(this);
  	}
  	
	public final native JsArray<VersionData> ConvertVersionInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}