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

import java.util.HashMap;

import opus.gwt.management.console.client.dashboard.ProjectManager;
import opus.gwt.management.console.client.deployer.ProjectDeployer;
import opus.gwt.management.console.client.event.AuthenticationSuccessEvent;
import opus.gwt.management.console.client.event.AuthenticationSuccessEventHandler;
import opus.gwt.management.console.client.event.CheckAuthenticationEvent;
import opus.gwt.management.console.client.navigation.NavigationPanel;
import opus.gwt.management.console.client.overlays.ProjectNames;
import opus.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;


public class PanelManager extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT.create(ManagementConsoleUiBinder.class);
	interface ManagementConsoleUiBinder extends UiBinder<Widget, PanelManager> {}

	private final String logoutURL = "/accounts/logout/";
	private final String checkLoginURL = "/json/username/?a&callback=";
	private final String projectsURL = "/json/?a&callback=";
	
	private Authentication authenticationPanel;
	private HandlerManager eventBus;
	
	private ProjectDeployer projectDeployer;
	private ProjectManager projectManager;
	private IconPanel iconPanel;
	private ServerCommunicator serverComm;
	private PanelManager panelManager;
	private JSVariableHandler JSVarHandler;
	private PopupPanel projectListPopup;
	private int projectCount;
	private String deletedProject;
	private HashMap<String, Integer> mainPanels;
	
	@UiField Label titleBarLabel;
	@UiField FlowPanel navigationMenuPanel;
	@UiField ManagementConsoleStyle style;
	@UiField Button deployNewButton;
	@UiField Button dashboardsButton;
	@UiField FlowPanel topMenuFlowPanel;
	@UiField Button loggedInUserButton;
	@UiField Button authenticationButton;
	@UiField DeckPanel mainDeckPanel;
	
	public PanelManager(HandlerManager eventBus, ServerCommunicator serverComm) {
		initWidget(uiBinder.createAndBindUi(this));
		this.serverComm = serverComm;
		this.eventBus = eventBus;
		panelManager = this;
		JSVarHandler = new JSVariableHandler();
		authenticationPanel = new Authentication(panelManager, eventBus);
		projectDeployer = new ProjectDeployer(panelManager, eventBus);
		projectManager = new ProjectManager(panelManager);
		handleAuthentication();
		//deployProject();
		//manageProjects();
		//iconPanel = new IconPanel(this);
		//deletedProject = "";
		//projectListPopup = new PopupPanel();
		//setupProjectPopup();	
	}
	
	private void handleAuthentication(){
		eventBus.addHandler(AuthenticationSuccessEvent.TYPE, 
				new AuthenticationSuccessEventHandler(){
					public void onAuthenticationSuccess(AuthenticationSuccessEvent event){
						deployProject();
					}
		});
		eventBus.fireEvent(new CheckAuthenticationEvent());
		mainDeckPanel.insert(authenticationPanel, 0);
		mainDeckPanel.showWidget(0);
	}
	
	private void deployProject(){
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
	
	private void setupProjectPopup(){
		projectListPopup.setAutoHideEnabled(true);
		projectListPopup.addCloseHandler(new CloseHandler<PopupPanel>(){
			public void onClose(CloseEvent<PopupPanel> event){
				dashboardsButton.setStyleName(style.topDashboardButton());
			}
		});
	}
	
	private void createDashboardsPopup(){
		final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + projectsURL);
		serverComm.getJson(url, "handleProjectNames", this);	
	}
	
	public void onDeployNewProject(String projectName){
		createDashboardsPopup();
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
    	projectManager = new ProjectManager(panelManager);
	}
	
	public void onProjectDelete(String deletedProject){
		this.deletedProject = deletedProject;
		createDashboardsPopup();
		iconPanel.removeProjectIcon(deletedProject);
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
	}
	
	public ServerCommunicator getServerCommunicator(){
		return serverComm;
	}
	
	public JSVariableHandler getJSVariableHandler(){
		return JSVarHandler;
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewProjectClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		projectDeployer = new ProjectDeployer(panelManager, eventBus);
	}
	
	@UiHandler("dashboardsButton")
	void handleDashboardsButtonMouseOver(MouseOverEvent event){
		if(projectCount > 0) {
			dashboardsButton.setStyleName(style.topDashboardButtonActive());
			int left = dashboardsButton.getAbsoluteLeft();
			int top = dashboardsButton.getAbsoluteTop() + dashboardsButton.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			int width = dashboardsButton.getOffsetWidth();
			projectListPopup.setWidth(Integer.toString(width) + "px");
			projectListPopup.show();
		}
	}
	
	@UiHandler("dashboardsButton")
	void handleDashboardsButtonClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
		mainDeckPanel.add(iconPanel);
		mainDeckPanel.showWidget(0);
		if(projectListPopup.isShowing()){
			projectListPopup.hide();
		} else {
			dashboardsButton.setStyleName(style.topDashboardButtonActive());
			int left = dashboardsButton.getAbsoluteLeft();
			int top = dashboardsButton.getAbsoluteTop() + dashboardsButton.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			int width = dashboardsButton.getOffsetWidth();
			projectListPopup.setWidth(Integer.toString(width) + "px");
			projectListPopup.show();
		}
		projectListPopup.hide();
	}
	
	@UiHandler("authenticationButton")
	void handleAuthenticationButton(ClickEvent event){
		if(authenticationButton.getText().equals("Logout")){
			FormPanel logoutForm = new FormPanel();
			logoutForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
			      public void onSubmitComplete(SubmitCompleteEvent event) {
			        handleAuthentication();
			      }
			 });
			logoutForm.setMethod(FormPanel.METHOD_GET);
			logoutForm.setAction(JSVarHandler.getDeployerBaseURL() + logoutURL);
			mainDeckPanel.add(logoutForm);
			logoutForm.submit();
		} else {
			showLoginPanel();
		}
	}
	
	public void handleProjectNames(JsArray<ProjectNames> ProjectNames){
		projectListPopup.clear();
		projectCount = ProjectNames.length();
		iconPanel.projectIconsFlowPanel.clear();
		if(projectCount != 0){
			FlowPanel FP = new FlowPanel();
			for(int i = 0; i < ProjectNames.length(); i++){
				if( !ProjectNames.get(i).getName().equals(deletedProject)){
					final Label testLabel = new Label(ProjectNames.get(i).getName());
					testLabel.setStyleName(style.popupLabel());
					if( i == ProjectNames.length() - 1 ){
						testLabel.addStyleName(style.lastLabel());	
						testLabel.addMouseOverHandler(new MouseOverHandler(){
							public void onMouseOver(MouseOverEvent event){
								testLabel.setStyleName(style.popupLabelActive());
								testLabel.addStyleName(style.lastLabel());
							}
						});
						testLabel.addMouseOutHandler(new MouseOutHandler(){
							public void onMouseOut(MouseOutEvent event){
								testLabel.setStyleName(style.popupLabel());
								testLabel.addStyleName(style.lastLabel());
							}
						});
					} else {
					testLabel.addMouseOverHandler(new MouseOverHandler(){
						public void onMouseOver(MouseOverEvent event){
								testLabel.setStyleName(style.popupLabelActive());
							}
						});
						testLabel.addMouseOutHandler(new MouseOutHandler(){
							public void onMouseOut(MouseOutEvent event){
								testLabel.setStyleName(style.popupLabel());
							}
						});
					}
					testLabel.addClickHandler(new ClickHandler() {
				        public void onClick(ClickEvent event) {
				        	mainDeckPanel.clear();
				    		navigationMenuPanel.clear();
				        	projectManager = new ProjectManager(panelManager); 
				        	if(projectListPopup.isShowing()){
				    			dashboardsButton.setStyleName(style.topDashboardButton());
				    			projectListPopup.hide();
				    		}   	
				        }
				     });
					FP.add(testLabel);
					iconPanel.addProjectIcon(ProjectNames.get(i).getName());
				}
			}
			projectListPopup.add(FP);
			mainDeckPanel.add(iconPanel);
			mainDeckPanel.showWidget(0);
		} else {
			
			deployNewButton.click();
		}
		projectListPopup.setStyleName(style.dashboardsPopup());
	}
		
	private void showLoginPanel(){
		mainDeckPanel.clear();
		titleBarLabel.setText("");
		navigationMenuPanel.clear();
		loggedInUserButton.setVisible(false);
		authenticationButton.setVisible(false);
		dashboardsButton.setVisible(false);
		deployNewButton.setVisible(false);
		authenticationPanel = new Authentication(panelManager, eventBus);
		mainDeckPanel.add(authenticationPanel);
		mainDeckPanel.showWidget(0);
	}
}
