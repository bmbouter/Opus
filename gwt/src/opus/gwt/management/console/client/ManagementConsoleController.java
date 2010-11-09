package opus.gwt.management.console.client;

import java.util.HashMap;

import opus.gwt.management.console.client.event.AddProjectEvent;
import opus.gwt.management.console.client.event.AddProjectEventHandler;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.DataReadyEvent;
import opus.gwt.management.console.client.event.DeleteProjectEvent;
import opus.gwt.management.console.client.event.DeleteProjectEventHandler;
import opus.gwt.management.console.client.event.GetApplicationsEvent;
import opus.gwt.management.console.client.event.GetApplicationsEventHandler;
import opus.gwt.management.console.client.event.GetDjangoPackagesEvent;
import opus.gwt.management.console.client.event.GetDjangoPackagesEventHandler;
import opus.gwt.management.console.client.event.GetProjectsEvent;
import opus.gwt.management.console.client.event.GetProjectsEventHandler;
import opus.gwt.management.console.client.event.GetUserEvent;
import opus.gwt.management.console.client.event.GetUserEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.Window;


public class ManagementConsoleController {

	private boolean projectsReady;
	private boolean userReady;
	private boolean djangoPackagesReady;
	private boolean applicationsReady;
	private ClientFactory clientFactory;
	private EventBus eventBus;
	
	public ManagementConsoleController(ClientFactory clientFactory){
		this.clientFactory = clientFactory;
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
		eventBus.fireEvent(new AsyncRequestEvent("getProjects"));
		eventBus.fireEvent(new AsyncRequestEvent("getApplications"));
		eventBus.fireEvent(new AsyncRequestEvent("getUser"));
		eventBus.fireEvent(new AsyncRequestEvent("getDjangoPackages"));
	}
	
	private void registerHandlers(){
		eventBus.addHandler(GetApplicationsEvent.TYPE, 
			new GetApplicationsEventHandler() {
				public void onGetApplications(GetApplicationsEvent event) {
					clientFactory.setApplications(event.getApplications());
					applicationsReady = true;
					start();
				}
		});
		eventBus.addHandler(GetDjangoPackagesEvent.TYPE, 
			new GetDjangoPackagesEventHandler() {
				public void onGetDjangoPackages(GetDjangoPackagesEvent event) {
					clientFactory.setDjangoPackages(event.getDjangoPackages());
					djangoPackagesReady = true;
					start();
				}
		});
		eventBus.addHandler(GetUserEvent.TYPE, 
			new GetUserEventHandler() {
				public void onGetUser(GetUserEvent event) {
					clientFactory.setUser(event.getUser());
					userReady = true;
					start();
				}
		});
		eventBus.addHandler(GetProjectsEvent.TYPE, 
			new GetProjectsEventHandler(){
				public void onGetProjects(GetProjectsEvent event) {
					clientFactory.setProjects(event.getProjects());
					projectsReady = true;
					start();
				}
		});
		eventBus.addHandler(AddProjectEvent.TYPE, 
				new AddProjectEventHandler(){
					public void onAddProject(AddProjectEvent event) {
						clientFactory.getProjects().put(event.getProject().getName(), event.getProject());
						eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DASHBOARD, event.getProject().getName()));
					}
		});
		eventBus.addHandler(DeleteProjectEvent.TYPE, 
				new DeleteProjectEventHandler(){
					public void onDeleteProject(DeleteProjectEvent event) {
						clientFactory.getProjects().remove(event.getProjectName());
						eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.PROJECTS));
					}
		});
	}
	
	private void start(){
		if(projectsReady && applicationsReady && userReady && djangoPackagesReady){
			ManagementConsole mc = new ManagementConsole(clientFactory);
		}
	}
}
