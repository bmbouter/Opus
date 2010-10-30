package opus.gwt.management.console.client.event;


import com.google.gwt.event.shared.GwtEvent;


public class DataReadyEvent extends GwtEvent<DataReadyEventHandler> {
	
	public static Type<DataReadyEventHandler> TYPE = new Type<DataReadyEventHandler>();
	
	public DataReadyEvent(){}
	
  	@Override
  	public Type<DataReadyEventHandler> getAssociatedType() {
  		return TYPE;
  	}

  	@Override
  	protected void dispatch(DataReadyEventHandler handler) {
  		handler.onDataReady(this);
  	}
}
