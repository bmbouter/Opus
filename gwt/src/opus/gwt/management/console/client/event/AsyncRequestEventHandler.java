package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface AsyncRequestEventHandler extends EventHandler {
	void onAsyncRequest(AsyncRequestEvent event);
}
