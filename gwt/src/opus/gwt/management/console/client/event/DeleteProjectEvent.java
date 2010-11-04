package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;


public class DeleteProjectEvent extends GwtEvent<DeleteProjectEventHandler> {
	
	public static Type<DeleteProjectEventHandler> TYPE = new Type<DeleteProjectEventHandler>();
	private String projectName;
	
	public DeleteProjectEvent(String projectName){
		this.projectName = projectName;
	}
	
	public String getProjectName(){
		return projectName;
	}
	
  	@Override
  	public Type<DeleteProjectEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(DeleteProjectEventHandler handler) {
  		handler.onDeleteProject(this);
  	}
}
