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

import opus.gwt.management.console.client.dashboard.ProjectManager;
import opus.gwt.management.console.client.deployer.ProjectDeployer;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.AuthenticationSuccessEvent;
import opus.gwt.management.console.client.event.AuthenticationSuccessEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.navigation.NavigationPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.Widget;


public class PanelManager extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT.create(ManagementConsoleUiBinder.class);
	interface ManagementConsoleUiBinder extends UiBinder<Widget, PanelManager> {}
	
	private HandlerManager eventBus;
	private Authentication authenticationPanel;
	private ProjectDeployer projectDeployer;
	private ProjectManager projectManager;
	private IconPanel iconPanel;
	
	@UiField DeckPanel mainDeckPanel;
	@UiField NavigationPanel navigationPanel;
	
	public PanelManager(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		navigationPanel.setEventBus(eventBus);
		registerEvents();
		authenticationPanel = new Authentication(eventBus);
		projectDeployer = new ProjectDeployer(eventBus);
		projectManager = new ProjectManager(eventBus);
		eventBus.fireEvent(new AsyncRequestEvent("handleUser"));
		//deployProject();
		//manageProjects(); 
	}
	
	private void registerEvents(){
		eventBus.addHandler(AuthenticationSuccessEvent.TYPE, 
			new AuthenticationSuccessEventHandler(){
				public void onAuthenticationSuccess(AuthenticationSuccessEvent event){
					showDeployer();
				}
		});
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType().equals("deploy") ){
						showDeployer();
					}
				}
		});
	}
	
	private void showAuthentication(){
		mainDeckPanel.insert(authenticationPanel, 0);
		mainDeckPanel.showWidget(0);
	}
	
	private void showDeployer(){
		projectDeployer = new ProjectDeployer(eventBus);
		mainDeckPanel.clear();
		mainDeckPanel.insert(projectDeployer, 0);
		mainDeckPanel.showWidget(0);
	}
	
	private void manageProjects(){
		mainDeckPanel.insert(projectManager, 0);
		mainDeckPanel.showWidget(0);
	}	
	
	public void showPanel(Object panel){
		mainDeckPanel.showWidget(mainDeckPanel.getWidgetIndex((Widget) panel));
	}
}
