package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.UserInformation;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class UserInfoEvent extends GwtEvent<UserInfoEventHandler> {
	
	public static Type<UserInfoEventHandler> TYPE = new Type<UserInfoEventHandler>();
	private final UserInformation userInfo;
	
	public UserInfoEvent(JavaScriptObject userInfo){
		this.userInfo = ConvertUserInformation(userInfo);
	}
	
	public UserInformation getUserInfo(){
		return userInfo;
	}
	
  	@Override
  	public Type<UserInfoEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UserInfoEventHandler handler) {
	  handler.onUserInfo(this);
  	}
  	
	public final native UserInformation ConvertUserInformation(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}