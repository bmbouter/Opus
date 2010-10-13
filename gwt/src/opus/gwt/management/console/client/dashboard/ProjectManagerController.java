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

import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.navigation.BreadCrumbsPanel;
import opus.gwt.management.console.client.resources.ProjectManagerCss.ProjectManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.Widget;

public class ProjectManagerController extends Composite {

	private static ProjectDashboardUiBinder uiBinder = GWT.create(ProjectDashboardUiBinder.class);
	interface ProjectDashboardUiBinder extends UiBinder<Widget, ProjectManagerController> {}

	private DashboardPanel dashboardPanel;
	private DeleteProjectPanel deleteProjectPanel;
	private ManageApps manageApps;
	private ProjectSettingsPanel projectSettingsPanel;
	private HandlerManager eventBus;
	private String projectName;
	
	@UiField ProjectManagerStyle style;
	@UiField DeckPanel managerDeckPanel;
	
	public ProjectManagerController(HandlerManager eventBus, String projectName){
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		this.projectName = projectName;
		this.dashboardPanel = new DashboardPanel(eventBus);
		this.deleteProjectPanel = new DeleteProjectPanel(eventBus);
		//manageApps = new ManageApps();
		this.projectSettingsPanel = new ProjectSettingsPanel(this);
		setupmanagerDeckPanel();
		registerEvents();
		setupBreadCrumbs();
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {projectName, dashboardPanel.getTitle()};
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_CRUMBS, crumbs));
	}
	
	private void registerEvents(){
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
				new PanelTransitionEventHandler(){
					public void onPanelTransition(PanelTransitionEvent event){
						if( event.getTransitionType().equals("next") ){
							Widget panel =  event.getPanel();
							managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(panel) + 1);
							eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, managerDeckPanel.getWidget(managerDeckPanel.getVisibleWidget()).getTitle()));
						} else if( event.getTransitionType().equals("previous") ){
							Widget panel =  event.getPanel();
							managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(panel) - 1);
							eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, managerDeckPanel.getWidget(managerDeckPanel.getVisibleWidget()).getTitle()));
						}
					}
			});
	}
	
	private void setupmanagerDeckPanel(){
		managerDeckPanel.add(dashboardPanel);
		dashboardPanel.setTitle("Dashboard");
		//managerDeckPanel.add(manageApps);
		//managerDeckPanel.add(new HTML());
		managerDeckPanel.add(deleteProjectPanel);
		deleteProjectPanel.setTitle("Delete Project");
		managerDeckPanel.add(projectSettingsPanel);
		projectSettingsPanel.setTitle("Project Settings");
		managerDeckPanel.showWidget(0);
	}
}