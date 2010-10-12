package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class AuthenticationEvent extends GwtEvent<AuthenticationEventHandler> {
	
	public static Type<AuthenticationEventHandler> TYPE = new Type<AuthenticationEventHandler>();
	private boolean authenticated;
	private String username;
	
	public AuthenticationEvent(boolean authenticated, String username){
		this.username = username;
		this.authenticated = authenticated;
	}
	
	public boolean isAuthenticated(){
		return authenticated;
	}
	
	public String getUsername(){
		return username;
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
