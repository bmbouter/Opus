package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface AuthenticationEventHandler extends EventHandler {
	void onAuthentication(AuthenticationEvent event);
}
