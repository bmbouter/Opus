package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.ProjectInformation;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateProjectInformationEvent extends GwtEvent<UpdateProjectInformationEventHandler> {
	
	public static Type<UpdateProjectInformationEventHandler> TYPE = new Type<UpdateProjectInformationEventHandler>();
	private ProjectInformation projectInfo;
	
	public UpdateProjectInformationEvent(JavaScriptObject jso){
		this.projectInfo = ConvertProjectInformation(jso);
	}
	
	public ProjectInformation getProjectInformation(){
		return projectInfo;
	}
	
  	@Override
  	public Type<UpdateProjectInformationEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateProjectInformationEventHandler handler) {
	  handler.onUpdateProjectInformation(this);
  	}
	
	public final native ProjectInformation ConvertProjectInformation(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}