package opus.gwt.management.console.client;

import java.util.HashMap;

import com.google.gwt.event.shared.EventBus;

import opus.gwt.management.console.client.event.AddProjectEvent;
import opus.gwt.management.console.client.event.AddProjectEventHandler;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.DataReadyEvent;
import opus.gwt.management.console.client.event.DeleteProjectEvent;
import opus.gwt.management.console.client.event.DeleteProjectEventHandler;
import opus.gwt.management.console.client.event.GetApplicationsEvent;
import opus.gwt.management.console.client.event.GetApplicationsEventHandler;
import opus.gwt.management.console.client.event.GetProjectsEvent;
import opus.gwt.management.console.client.event.GetProjectsEventHandler;
import opus.gwt.management.console.client.event.GetUserEvent;
import opus.gwt.management.console.client.event.GetUserEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.Project;


public class ModelController {

	private ClientFactory clientFactory;
	private EventBus eventBus;
	
	public ModelController(ClientFactory clientFactory){
		this.clientFactory = clientFactory;
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(GetApplicationsEvent.TYPE, 
			new GetApplicationsEventHandler() {
				public void onGetApplications(GetApplicationsEvent event) {
					HashMap<String, Application> applications = event.getApplications();
					clientFactory.setApplications(applications);
					eventBus.fireEvent(new DataReadyEvent());
				}
		});
		eventBus.addHandler(GetUserEvent.TYPE, 
				new GetUserEventHandler() {
					public void onGetUser(GetUserEvent event) {
						clientFactory.setUser(event.getUser());
						eventBus.fireEvent(new AsyncRequestEvent("getProjects"));
					}
		});
		eventBus.addHandler(GetProjectsEvent.TYPE, 
			new GetProjectsEventHandler(){
				public void onGetProjects(GetProjectsEvent event) {
					HashMap<String, Project> projects = event.getProjects();
					clientFactory.setProjects(projects);
					eventBus.fireEvent(new AsyncRequestEvent("getApplications"));
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
	
}
