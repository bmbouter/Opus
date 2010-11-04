package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class AddProjectEvent extends GwtEvent<AddProjectEventHandler> {
	
	public static Type<AddProjectEventHandler> TYPE = new Type<AddProjectEventHandler>();
	private Project project;
	
	public AddProjectEvent(JavaScriptObject jso){
		this.project = ConvertProject(jso);
	}
	
	public Project getProject(){
		return project;
	}
	
  	@Override
  	public Type<AddProjectEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(AddProjectEventHandler handler) {
  		handler.onAddProject(this);
  	}
	
	private final native Project ConvertProject(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}