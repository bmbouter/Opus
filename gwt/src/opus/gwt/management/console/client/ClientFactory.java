package opus.gwt.management.console.client;

import opus.gwt.management.console.client.ClientFactory;
import com.google.gwt.event.shared.EventBus;

public interface ClientFactory {
	EventBus getEventBus();
	JSVariableHandler getJSVariableHandler();
}
