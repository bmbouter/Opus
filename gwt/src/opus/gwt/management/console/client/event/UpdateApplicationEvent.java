package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.deployer.Application;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateApplicationEvent extends GwtEvent<UpdateApplicationEventHandler> {
	
	public static Type<UpdateApplicationEventHandler> TYPE = new Type<UpdateApplicationEventHandler>();
	private JsArray<Application> application;
	
	public UpdateApplicationEvent(JavaScriptObject appInfo){
		this.application = ConvertAppInfo(appInfo);
	}
	
	public JsArray<Application> getAppInfo(){
		return application;
	}
	
  	@Override
  	public Type<UpdateApplicationEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateApplicationEventHandler handler) {
	  handler.onUpdateAppInfo(this);
  	}
  	
	public final native JsArray<Application> ConvertAppInfo(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}