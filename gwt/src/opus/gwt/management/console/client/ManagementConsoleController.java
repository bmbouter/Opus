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

package opus.gwt.management.console.client;

import opus.gwt.management.console.client.dashboard.IconPanel;
import opus.gwt.management.console.client.dashboard.ProjectManagerController;
import opus.gwt.management.console.client.dashboard.ProjectSettingsPanel;
import opus.gwt.management.console.client.deployer.ProjectDeployerController;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.AuthenticationEvent;
import opus.gwt.management.console.client.event.AuthenticationEventHandler;
import opus.gwt.management.console.client.event.DataReadyEvent;
import opus.gwt.management.console.client.event.DataReadyEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.navigation.BreadCrumbsPanel;
import opus.gwt.management.console.client.navigation.NavigationPanel;
import opus.gwt.management.console.client.resources.ManagementConsoleControllerResources.ManagementConsoleControllerStyle;
import opus.gwt.management.console.client.tools.AuthenticationPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.RootLayoutPanel;
import com.google.gwt.user.client.ui.Widget;


public class ManagementConsoleController extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT.create(ManagementConsoleUiBinder.class);
	interface ManagementConsoleUiBinder extends UiBinder<Widget, ManagementConsoleController> {}
	
	private EventBus eventBus;
	private ClientFactory clientFactory;
	private AuthenticationPanel authenticationPanel;
	private ProjectDeployerController projectDeployerController;
	private ProjectManagerController projectManagerController;
	private JSVariableHandler jsVarHandler;

	
	@UiField LayoutPanel contentLayoutPanel;
	@UiField NavigationPanel navigationPanel;
	@UiField BreadCrumbsPanel breadCrumbsPanel;
	@UiField ManagementConsoleControllerStyle style;
	
	public ManagementConsoleController(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		RootLayoutPanel.get().setStyleName(style.rootLayoutPanel());
		this.clientFactory = clientFactory;
		this.jsVarHandler = clientFactory.getJSVariableHandler();
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
		checkAuthentication();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(DataReadyEvent.TYPE, 
				new DataReadyEventHandler(){
					public void onDataReady(DataReadyEvent event) {
						startConsole();
					}
		});
		eventBus.addHandler(AuthenticationEvent.TYPE, 
				new AuthenticationEventHandler(){
					public void onAuthentication(AuthenticationEvent event) {
						eventBus.fireEvent(new AsyncRequestEvent("getUser"));
					}
		});
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.DEPLOY ){
						showDeployer();
					} else if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.PROJECTS ){
						showIconPanel();
					} else if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.DASHBOARD ){
						manageProjects(event.getName());
					}
				}
		});
	}
	
	private void checkAuthentication(){
		if( jsVarHandler.getUser().equals("") ){
			contentLayoutPanel.clear();
			RootLayoutPanel.get().add(new AuthenticationPanel(clientFactory));			
		} else {
			eventBus.fireEvent(new AsyncRequestEvent("getUser"));
		}
	}
	
	private void startConsole(){
		navigationPanel.setClientFactory(clientFactory);
		breadCrumbsPanel.setClientFactory(clientFactory);
		if( clientFactory.getProjects().size() > 0 ){
			if( jsVarHandler.getProjectToken() != null ){
				showDeployer();
			} else {
				showIconPanel();
			}
		} else {
			showDeployer();
		}
	}
	
	private void showDeployer(){
		RootLayoutPanel.get().clear();
		RootLayoutPanel.get().add(this);
		projectDeployerController = new ProjectDeployerController(clientFactory);
		contentLayoutPanel.clear();
		contentLayoutPanel.add(projectDeployerController);
		contentLayoutPanel.setVisible(true);
	}
	
	private void manageProjects(String projectName){
		RootLayoutPanel.get().clear();
		RootLayoutPanel.get().add(this);
		projectManagerController = new ProjectManagerController(clientFactory, projectName);
		contentLayoutPanel.clear();
		contentLayoutPanel.add(projectManagerController);
		contentLayoutPanel.setVisible(true);
	}
	
	private void showIconPanel(){
		RootLayoutPanel.get().clear();
		RootLayoutPanel.get().add(this);
		IconPanel iconPanel = new IconPanel(clientFactory);
		contentLayoutPanel.clear();
		contentLayoutPanel.add(iconPanel);
		contentLayoutPanel.setVisible(true);
	}
}
