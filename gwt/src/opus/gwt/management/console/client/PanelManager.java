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
import opus.gwt.management.console.client.event.AuthenticationEvent;
import opus.gwt.management.console.client.event.AuthenticationEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.navigation.BreadCrumbs;
import opus.gwt.management.console.client.navigation.NavigationPanel;
import opus.gwt.management.console.client.resources.PanelManagerCss.PanelManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.RootLayoutPanel;
import com.google.gwt.user.client.ui.Widget;


public class PanelManager extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT.create(ManagementConsoleUiBinder.class);
	interface ManagementConsoleUiBinder extends UiBinder<Widget, PanelManager> {}
	
	private HandlerManager eventBus;
	private Authentication authenticationPanel;
	private ProjectDeployer projectDeployer;
	private ProjectManager projectManager;
	private IconPanel iconPanel;
	
	@UiField LayoutPanel contentLayoutPanel;
	@UiField NavigationPanel navigationPanel;
	@UiField BreadCrumbs breadCrumbs;
	@UiField PanelManagerStyle style;
	
	public PanelManager(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		RootLayoutPanel.get().setStyleName(style.rootLayoutPanel());
		this.eventBus = eventBus;
		navigationPanel.setEventBus(eventBus);
		breadCrumbs.setEventBus(eventBus);
		iconPanel = new IconPanel(eventBus);
		registerEvents();
		authenticationPanel = new Authentication(eventBus);
		eventBus.fireEvent(new AsyncRequestEvent("handleUser"));
	}
	
	private void registerEvents(){
		eventBus.addHandler(AuthenticationEvent.TYPE, 
			new AuthenticationEventHandler(){
				public void onAuthentication(AuthenticationEvent event){
					if( event.isAuthenticated() ){
						showDeployer();
					} else if ( !event.isAuthenticated() ){
						showAuthentication();
					}
				}
		});
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType().equals("deploy") ){
						showDeployer();
					} else if( event.getTransitionType().equals("projects") ){
						showIconPanel();
					}
				}
		});
	}
	
	private void showAuthentication(){
		contentLayoutPanel.clear();
		contentLayoutPanel.add(authenticationPanel);
		RootLayoutPanel.get().add(authenticationPanel);
	}
	
	private void showDeployer(){
		RootLayoutPanel.get().clear();
		RootLayoutPanel.get().add(this);
		projectDeployer = new ProjectDeployer(eventBus);
		contentLayoutPanel.clear();
		contentLayoutPanel.add(projectDeployer);
		contentLayoutPanel.setVisible(true);
	}
	
	/*
	private void manageProjects(){
		projectManager = new ProjectManager(eventBus);
		//mainDeckPanel.insert(projectManager, 0);
		//mainDeckPanel.showWidget(0);
	}
	*/
	private void showIconPanel(){
		contentLayoutPanel.clear();
		contentLayoutPanel.add(iconPanel);
		contentLayoutPanel.setVisible(true);
		//mainDeckPanel.showWidget(0);
	}
}
