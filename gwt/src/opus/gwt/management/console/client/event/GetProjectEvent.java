package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class GetProjectEvent extends GwtEvent<GetProjectEventHandler> {
	public static Type<GetProjectEventHandler> TYPE = new Type<GetProjectEventHandler>();
	private Project project;
	
	public GetProjectEvent(JavaScriptObject jso){
		this.project = ConvertProject(jso);
	}
	
	public Project getProject(){
		return project;
	}
	
  	@Override
  	public Type<GetProjectEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(GetProjectEventHandler handler) {
  		handler.onGetProject(this);
  	}
	
	private final native Project ConvertProject(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}