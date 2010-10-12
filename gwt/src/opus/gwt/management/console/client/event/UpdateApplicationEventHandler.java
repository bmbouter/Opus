package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface UpdateApplicationEventHandler extends EventHandler {
	void onUpdateAppInfo(UpdateApplicationEvent event);
}
