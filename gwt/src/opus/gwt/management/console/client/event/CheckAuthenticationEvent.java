package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.UserInformation;

import com.google.gwt.core.client.JavaScriptObject;
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