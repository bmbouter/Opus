package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface DataReadyEventHandler extends EventHandler {
	void onDataReady(DataReadyEvent event);
}
