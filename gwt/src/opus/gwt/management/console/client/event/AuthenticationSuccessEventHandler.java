package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface AuthenticationSuccessEventHandler extends EventHandler {
	void onAuthenticationSuccess(AuthenticationSuccessEvent event);
}
