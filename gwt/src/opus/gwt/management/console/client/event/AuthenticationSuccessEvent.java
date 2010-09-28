package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class AuthenticationSuccessEvent extends GwtEvent<AuthenticationSuccessEventHandler> {
	
	public static Type<AuthenticationSuccessEventHandler> TYPE = new Type<AuthenticationSuccessEventHandler>();
	
	@Override
  	public Type<AuthenticationSuccessEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(AuthenticationSuccessEventHandler handler) {
	  handler.onAuthenticationSuccess(this);
  	}
}
