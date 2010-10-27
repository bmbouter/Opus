package opus.gwt.management.console.client;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ClientFactory;
import com.google.gwt.event.shared.EventBus;

public interface ClientFactory {
	EventBus getEventBus();
	JSVariableHandler getJSVariableHandler();
	void setApplications(HashMap<String, Application> applications);
	HashMap<String, Application> getApplications();
	void setProjects(HashMap<String, Project> projects);
	HashMap<String, Project> getProjects();
}
