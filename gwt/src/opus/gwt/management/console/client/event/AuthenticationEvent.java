package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class AuthenticationEvent extends GwtEvent<AuthenticationEventHandler> {
	
	public static Type<AuthenticationEventHandler> TYPE = new Type<AuthenticationEventHandler>();
	
	public AuthenticationEvent(){
	}
	
	@Override
  	public Type<AuthenticationEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(AuthenticationEventHandler handler) {
	  handler.onAuthentication(this);
  	}
}
