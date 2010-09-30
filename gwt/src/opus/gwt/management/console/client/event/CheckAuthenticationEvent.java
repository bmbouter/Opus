package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;


public class CheckAuthenticationEvent extends GwtEvent<CheckAuthenticationEventHandler> {
	
	public static Type<CheckAuthenticationEventHandler> TYPE = new Type<CheckAuthenticationEventHandler>();
	
	public CheckAuthenticationEvent(){
	}
	
  	@Override
  	public Type<CheckAuthenticationEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(CheckAuthenticationEventHandler handler) {
	  handler.onCheckAuthentication(this);
  	}
}