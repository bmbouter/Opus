package opus.gwt.management.console.client.event;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class GetProjectsEvent extends GwtEvent<GetProjectsEventHandler> {
	public static Type<GetProjectsEventHandler> TYPE = new Type<GetProjectsEventHandler>();
	private JsArray<Project> projectsArray;
	private HashMap<String, Project> projectsMap = new HashMap<String, Project>();
	
	public GetProjectsEvent(JavaScriptObject jso){
		this.projectsArray = ConvertProjects(jso);
		processProjects();
	}
	
	private void processProjects() {
		for(int i = 0; i < projectsArray.length(); i++) {
			Project proj = projectsArray.get(i);
			projectsMap.put(proj.getName(), proj);
		}
	}
	
	public HashMap<String, Project> getProjects(){
		return projectsMap;
	}
	
  	@Override
  	public Type<GetProjectsEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(GetProjectsEventHandler handler) {
  		handler.onGetProjects(this);
  	}
	
	private final native JsArray<Project> ConvertProjects(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}