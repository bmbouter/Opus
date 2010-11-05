package opus.gwt.management.console.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.DjangoPackage;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.overlays.User;

import com.google.gwt.event.shared.EventBus;
import com.google.gwt.event.shared.SimpleEventBus;

public class ClientFactoryImpl implements ClientFactory {
	private final EventBus eventBus = new SimpleEventBus();
	private final JSVariableHandler jsVarHandler = new JSVariableHandler();
	private User user;
	private HashMap<String, Application> applications = null;
	private HashMap<String, Project> projects = null;
	private List<DjangoPackage> djangoPackages = new ArrayList<DjangoPackage>();
	
	@Override
	public EventBus getEventBus(){
		return eventBus;
	}
	
	@Override
	public JSVariableHandler getJSVariableHandler(){
		return jsVarHandler;
	}
	
	@Override
	public User getUser(){
		return user;
	}
	
	@Override
	public void setUser(User user){
		this.user = user;
	}

	@Override
	public HashMap<String, Application> getApplications() {
		return applications;
	}
	
	@Override
	public void setApplications(HashMap<String, Application> applications) {
		this.applications = applications;
	}
	
	@Override
	public HashMap<String, Project> getProjects() {
		return projects;
	}
	
	@Override
	public void setProjects(HashMap<String, Project> projects) {
		this.projects = projects;
	}
	
	@Override
	public List<DjangoPackage> getDjangoPackages() {
		return djangoPackages;
	}
	
	@Override
	public void setDjangoPackages(List<DjangoPackage> djangoPackages) {
		this.djangoPackages = djangoPackages;
	}
}
