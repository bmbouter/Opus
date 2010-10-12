package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateProjectsEvent extends GwtEvent<UpdateProjectsEventHandler> {
	
	public static Type<UpdateProjectsEventHandler> TYPE = new Type<UpdateProjectsEventHandler>();
	private JsArray<Project> projects;
	
	public UpdateProjectsEvent(JavaScriptObject jso){
		this.projects = ConvertProjects(jso);
	}
	
	public JsArray<Project> getProjects(){
		return projects;
	}
	
  	@Override
  	public Type<UpdateProjectsEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateProjectsEventHandler handler) {
  		handler.onUpdateProjects(this);
  	}
	
	private final native JsArray<Project> ConvertProjects(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}