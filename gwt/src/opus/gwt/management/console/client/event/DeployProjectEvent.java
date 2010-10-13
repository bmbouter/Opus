package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class DeployProjectEvent extends GwtEvent<DeployProjectEventHandler> {
	
	public static Type<DeployProjectEventHandler> TYPE = new Type<DeployProjectEventHandler>();
	
	public DeployProjectEvent(){
	}
	
  	@Override
  	public Type<DeployProjectEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(DeployProjectEventHandler handler) {
	  handler.onDeployProject(this);
  	}
}
