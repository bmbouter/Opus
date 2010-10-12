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

package opus.gwt.management.console.client.deployer;

import java.util.ArrayList;

import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;


public class ProjectDeployerController extends Composite {
	
	private static applicationDeployerUiBinder uiBinder = GWT.create(applicationDeployerUiBinder.class);
	interface applicationDeployerUiBinder extends UiBinder<Widget, ProjectDeployerController> {}
		
	private final String deploymentURL =  "/deployments/projectName/";
		
	private ProjectOptionsPanel projectOptionsPanel;
	private DatabaseOptionsPanel databaseOptionsPanel;
	private DeploymentOptionsPanel deploymentOptionsPanel;
	private ConfirmProject confirmBP;
	private AppBrowserPanel appBrowserPanel;
	private HandlerManager eventBus;
	private FormPanel deployerForm;
		
	@UiField ProjectDeployerStyle style;
	@UiField DeckPanel deployerDeckPanel;
	
	public ProjectDeployerController(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		this.deployerForm = new FormPanel();
		this.appBrowserPanel = new AppBrowserPanel(eventBus);
		this.projectOptionsPanel = new ProjectOptionsPanel(eventBus);
		this.databaseOptionsPanel = new DatabaseOptionsPanel(eventBus);
		this.deploymentOptionsPanel = new DeploymentOptionsPanel(eventBus);
		this.confirmBP = new ConfirmProject(deployerForm, eventBus);
		setupdeployerDeckPanel();
		registerEvents();
		setupBreadCrumbs();
		setupDeployerForm();
	}
	
	private void setupdeployerDeckPanel(){
		deployerDeckPanel.add(appBrowserPanel);
		deployerDeckPanel.add(projectOptionsPanel);
		deployerDeckPanel.add(databaseOptionsPanel);
		deployerDeckPanel.add(deploymentOptionsPanel);
		//deployerDeckPanel.add(confirmBP);
		deployerDeckPanel.add(deployerForm);
		appBrowserPanel.setTitle("Application Browser");
		projectOptionsPanel.setTitle("Project Options");
		databaseOptionsPanel.setTitle("Database Options");
		deploymentOptionsPanel.setTitle("Deployment Options");
		deployerDeckPanel.showWidget(0);
		appBrowserPanel.setHeight("");
		appBrowserPanel.setWidth("");
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {appBrowserPanel.getTitle(), projectOptionsPanel.getTitle(), databaseOptionsPanel.getTitle(), deploymentOptionsPanel.getTitle()};
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_CRUMBS, crumbs));
	}
	
	private void setupDeployerForm(){
		 deployerForm.setMethod(FormPanel.METHOD_POST);
		  deployerForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        //panelManager.onDeployNewProject(createdProjectName);
		      }
		    });
	}
	
	private void registerEvents(){
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.NEXT ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) + 1);
						eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
						setFocus(panel);
					} else if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.PREVIOUS ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) - 1);
						eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
					}
				}
		});
	}
	
	public void setFocus(Widget panel){
		if( panel.getClass().equals(databaseOptionsPanel.getClass()) ){
			deploymentOptionsPanel.setFocus();
		} else if( panel.getClass().equals(appBrowserPanel.getClass()) ){
			projectOptionsPanel.setFocus();
		} else if( panel.getClass().equals(projectOptionsPanel.getClass()) ){
			databaseOptionsPanel.setFocus();
		}
	}
	
	void handleConfirmBuildProjectLoad() {
		String username = projectOptionsPanel.usernameTextBox.getValue();
		String email = projectOptionsPanel.emailTextBox.getValue();
		
		String databaseEngine = databaseOptionsPanel.dbengineListBox.getItemText(databaseOptionsPanel.dbengineListBox.getSelectedIndex());
		String databaseName = databaseOptionsPanel.nameTextBox.getValue();
		String databasePassword = databaseOptionsPanel.passwordTextBox.getValue();
		String databaseHost = databaseOptionsPanel.hostTextBox.getValue();
		String databasePort = databaseOptionsPanel.portTextBox.getValue();
		
		String projectName = deploymentOptionsPanel.projectNameTextBox.getText() + deploymentOptionsPanel.baseProtocolLabel.getText();
		
		
		ArrayList<String> apps = appBrowserPanel.getApps();
		String html = "<p><b>List of Applications:</b> <ul>";
		
		for (int i = 0; i < apps.size(); i++){
			html += "<li>" + apps.get(i) + "</li>";
		}
		
		html += "</ul></p>";
		
		if (username.length() > 0 ) {
			html += "<p><b>Super Username:</b> " + username + "</p>";
		}
		if (email.length() > 0) {
			html += "<p><b>Email:</b> " + email + "</p>";
		}
		
		html += "<p><b>Django Admin Interface:</b>";
		
		if (!databaseEngine.contains("sqlite")){
			html += "<p><b>Database Engine:</b> " + databaseEngine + "</p>";
			html += "<p><b>DB Name:</b> " + databaseName +"</p>";
			html += "<p><b>DB Password:</b> " + databasePassword + "</p>";
			html += "<p><b>DB Host:</b> " + databaseHost + "</p>";
			html += "<p><b>DB Port:</b> " + databasePort + "</p>";
		} else {
			html += "<p><b>Database Engine:</b> " + databaseEngine + "</p>";
		}
		
		html += "<p><b>Deploy as: </b>" + projectName + "</p>";
			confirmBP.confirmationScrollPanel.clear();
			confirmBP.confirmationScrollPanel.add(new HTML(html,true));
	  }
	  
	  void handleConfirmDeployProject(){
		  deployerForm.setAction(deploymentURL.replaceAll("projectName", deploymentOptionsPanel.projectNameTextBox.getText())); 
		  //createdProjectName = deploymentOptionsPanel.projectNameTextBox.getText();
		  
		  VerticalPanel formContainerPanel = new VerticalPanel();
		  this.deployerForm.add(formContainerPanel);
		  
		  ArrayList<String> paths = appBrowserPanel.getAppPaths();
		  ArrayList<String> apptypes = appBrowserPanel.getAppTypes();
		  Hidden numApps = new Hidden();
		  numApps.setName("form-TOTAL_FORMS");
		  numApps.setValue(String.valueOf(paths.size()));
		  formContainerPanel.add(numApps);
		  Hidden numInitialForms = new Hidden();
		  numInitialForms.setName("form-INITIAL_FORMS");
		  numInitialForms.setValue("0");
		  Hidden numMaxForms = new Hidden();
		  numMaxForms.setName("form-MAX_NUM_FORMS");
		  formContainerPanel.add(numInitialForms);
		  formContainerPanel.add(numMaxForms);
		  for(int i=0; i < paths.size(); i++) {
			  //Window.alert(paths.get(i).toString());
			  RadioButton pathtype = new RadioButton("form-" + i + "-apptype");
			  pathtype.setFormValue(apptypes.get(i));
			  pathtype.setValue(true);
			  TextBox path = new TextBox();
			  path.setName("form-" + i +"-apppath");
			  path.setValue(paths.get(i));
			  formContainerPanel.add(pathtype);
			  formContainerPanel.add(path);
		  }
	  
		  CheckBox debug = deploymentOptionsPanel.debugCheckBox;
		  formContainerPanel.add(debug);
		  
		  //Add all project options fields to the form for submission
		  formContainerPanel.add(projectOptionsPanel.projectOptionsPanel);
		  
		  //Add all database options fields to the form for submission
		  formContainerPanel.add(databaseOptionsPanel.databaseOptionsPanel);
		 
		  //Add all Database fields to the form for submissionsd
		  formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
			  deployerForm.submit();
	  }
}
