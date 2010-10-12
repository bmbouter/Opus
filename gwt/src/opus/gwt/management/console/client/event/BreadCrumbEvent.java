package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class BreadCrumbEvent extends GwtEvent<BreadCrumbEventHandler> {
	
	public static Type<BreadCrumbEventHandler> TYPE = new Type<BreadCrumbEventHandler>();
	public enum Action{SET_CRUMBS, SET_ACTIVE, ADD_CRUMB, REMOVE_CRUMB};
	private Action actionType;
	private String[] names;
	private String crumb;
	
	public BreadCrumbEvent(Action actionType, String[] names){
		this.actionType = actionType;
		this.names = names;
	}
	
	public BreadCrumbEvent(Action actionType, String crumb){
		this.actionType = actionType;
		this.crumb = crumb;
	}
	
	public Action getAction(){
		return actionType;
	}

	public String getCrumb(){
		return crumb;
	}
	
	public String[] getCrumbNames(){
		return names;
	}
	
  	@Override
  	public Type<BreadCrumbEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(BreadCrumbEventHandler handler) {
	  handler.onBreadCrumb(this);
  	}
}
