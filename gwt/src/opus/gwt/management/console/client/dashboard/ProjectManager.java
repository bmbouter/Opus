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

import opus.gwt.management.console.client.navigation.BreadCrumbs;
import opus.gwt.management.console.client.resources.ProjectManagerCss.ProjectManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.Widget;

public class ProjectManager extends Composite {

	private static ProjectDashboardUiBinder uiBinder = GWT.create(ProjectDashboardUiBinder.class);
	interface ProjectDashboardUiBinder extends UiBinder<Widget, ProjectManager> {}

	private Dashboard dashboard;
	private DeleteProject deleteProject;
	private ManageApps manageApps;
	private ProjectSettings projectSettings;
	private HandlerManager eventBus;
	
	private int navigationMenuFocusFlag;
	private enum DeckPanels{DASHBOARDPANEL, DELETEPROJECTPANEL, OPTIONSPANEL};
	
	@UiField ProjectManagerStyle style;
	@UiField DeckPanel managerDeckPanel;
	@UiField BreadCrumbs breadCrumbs;
	
	public ProjectManager(HandlerManager eventBus){
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		dashboard = new Dashboard(this, eventBus);
		deleteProject = new DeleteProject(this);
		//manageApps = new ManageApps();
		projectSettings = new ProjectSettings(this);
		setupmanagerDeckPanel();
		setupBreadCrumbs();
	}
	
	private void setupmanagerDeckPanel(){
		managerDeckPanel.add(dashboard);
		dashboard.setTitle("Dashboard");
		//managerDeckPanel.add(manageApps);
		//managerDeckPanel.add(new HTML());
		managerDeckPanel.add(deleteProject);
		deleteProject.setTitle("Delete Project");
		managerDeckPanel.add(projectSettings);
		projectSettings.setTitle("Project Settings");
		managerDeckPanel.showWidget(0);
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {dashboard.getTitle(), deleteProject.getTitle(), projectSettings.getTitle()};
		breadCrumbs.setBreadCrumbs(crumbs);
		breadCrumbs.setActiveCrumb(crumbs[0]);
	}
	
	public ProjectSettings getOptionsPanel(){
		return this.projectSettings;
	}
	
	public void showNextPanel(Widget panel){
		managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(panel) + 1);
		breadCrumbs.setActiveCrumb(managerDeckPanel.getWidget(managerDeckPanel.getVisibleWidget()).getTitle());
	}

	public void showPreviousPanel(Widget panel){
		managerDeckPanel.showWidget(managerDeckPanel.getWidgetIndex(panel) - 1);
		breadCrumbs.setActiveCrumb(managerDeckPanel.getWidget(managerDeckPanel.getVisibleWidget()).getTitle());
	}
	
	public Dashboard getDashboard(){
		return dashboard;
	}
	
	public DeckPanel getDeckPanel(){
		return this.managerDeckPanel;
	}
}
