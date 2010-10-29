package opus.gwt.management.console.client.event;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateProjectsEvent extends GwtEvent<UpdateProjectsEventHandler> {
	
	public static Type<UpdateProjectsEventHandler> TYPE = new Type<UpdateProjectsEventHandler>();
	private HashMap<String, Project> projects;
	
	public UpdateProjectsEvent(JavaScriptObject jso){
		JsArray<Project> projs = ConvertProjects(jso);
		 for( int i =0; i < projs.length(); i++){
			 projects.put(projs.get(i).getName(), projs.get(i));
		 }
	}
	
	public HashMap<String, Project> getProjects(){
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