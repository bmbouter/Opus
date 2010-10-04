package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.DBOptions;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;
import com.google.gwt.event.shared.GwtEvent.Type;

public class BreadCrumbEvent extends GwtEvent<BreadCrumbEventHandler> {
	
	public static Type<BreadCrumbEventHandler> TYPE = new Type<BreadCrumbEventHandler>();
	private String eventType;
	private String[] names;
	private String active;
	
	public BreadCrumbEvent(String eventType, String[] names){
		this.eventType = eventType;
		this.names = names;
	}
	
	public BreadCrumbEvent(String eventType, String active){
		this.eventType = eventType;
		this.active = active;
	}
	
	public String getEventType(){
		return eventType;
	}

	public String getActive(){
		return active;
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
