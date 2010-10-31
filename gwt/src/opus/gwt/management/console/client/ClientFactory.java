package opus.gwt.management.console.client;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.DjangoPackage;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.overlays.User;

import com.google.gwt.event.shared.EventBus;

public interface ClientFactory {
	EventBus getEventBus();
	JSVariableHandler getJSVariableHandler();
	void setApplications(HashMap<String, Application> applications);
	HashMap<String, Application> getApplications();
	void setProjects(HashMap<String, Project> projects);
	HashMap<String, Project> getProjects();
	void setDjangoPackages(HashMap<String, DjangoPackage> djangoPackages);
	HashMap<String, DjangoPackage> getDjangoPackages();
	User getUser();
	void setUser(User user);
}
