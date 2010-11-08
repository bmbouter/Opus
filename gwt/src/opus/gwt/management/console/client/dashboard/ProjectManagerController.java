/*############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
############################################################################*/

package opus.gwt.management.console.client.dashboard;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.resources.ProjectManagerCss.ProjectManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.Widget;

public class ProjectManagerController extends Composite {

	private static ProjectDashboardUiBinder uiBinder = GWT.create(ProjectDashboardUiBinder.class);
	interface ProjectDashboardUiBinder extends UiBinder<Widget, ProjectManagerController> {}

	private DashboardPanel dashboardPanel;
	private DeleteProjectPanel deleteProjectPanel;
	private AppSettingsPanel appSettingsPanel;
	private EventBus eventBus;
	private String projectName;
	private ClientFactory clientFactory;
	
	@UiField ProjectManagerStyle style;
	@UiField DeckPanel managerDeckPanel;
	
	public ProjectManagerController(ClientFactory clientFactory, String projectName){
		initWidget(uiBinder.createAndBindUi(this));
		Window.alert("creating a project manager controller");
		this.clientFactory = clientFactory;
		this.eventBus = clientFactory.getEventBus();
		this.projectName = projectName;
		this.dashboardPanel = new DashboardPanel(clientFactory, projectName);
		this.deleteProjectPanel = new DeleteProjectPanel(clientFactory, projectName);
		this.appSettingsPanel = new AppSettingsPanel(clientFactory, projectName);
		setupmanagerDeckPanel();
		registerHandlers();
		setupBreadCrumbs();
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {"Projects", projectName, dashboardPanel.getTitle()};
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_CRUMBS, crumbs));
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, projectName));
	}
	
	private void registerHandlers(){
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
				new PanelTransitionEventHandler(){
					public void onPanelTransition(PanelTransitionEvent event){
						if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.SETTINGS ){
							Window.alert("received event in project manager controller to show app settings panel");
							managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(appSettingsPanel));
						} else if(event.getTransitionType() == PanelTransitionEvent.TransitionTypes.DELETE) {
							Window.alert("received event in project manager controller to show delete project panel");
							managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(deleteProjectPanel));
						}
					}
			});
	}
	
	private void setupmanagerDeckPanel(){
		Window.alert("adding all the panels in project manager controller");
		managerDeckPanel.add(dashboardPanel);
		dashboardPanel.setTitle("Dashboard");
		managerDeckPanel.add(deleteProjectPanel);
		deleteProjectPanel.setTitle("Delete Project");
		managerDeckPanel.add(appSettingsPanel);
		appSettingsPanel.setTitle("Application Settings");
		managerDeckPanel.showWidget(0);
	}
}
