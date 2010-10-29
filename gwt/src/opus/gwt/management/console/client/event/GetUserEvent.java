package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.User;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class GetUserEvent extends GwtEvent<GetUserEventHandler> {
	
	public static Type<GetUserEventHandler> TYPE = new Type<GetUserEventHandler>();
	private final User user;
	
	public GetUserEvent(JavaScriptObject user){
		this.user = ConvertUser(user);
	}
	
	public User getUser(){
		return user;
	}
	
  	@Override
  	public Type<GetUserEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(GetUserEventHandler handler) {
	  handler.onGetUser(this);
  	}
  	
	public final native User ConvertUser(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}