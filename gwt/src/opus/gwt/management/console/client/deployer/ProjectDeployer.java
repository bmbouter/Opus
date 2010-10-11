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


public class ProjectDeployer extends Composite {
	
	private static applicationDeployerUiBinder uiBinder = GWT.create(applicationDeployerUiBinder.class);
	interface applicationDeployerUiBinder extends UiBinder<Widget, ProjectDeployer> {}
		
	private final String deploymentURL =  "/deployments/projectName/";
		
	private ProjectOptions projectOptions;
	private DatabaseOptions databaseOptions;
	private DeploymentOptions deploymentOptions;
	private ConfirmProject confirmBP;
	private AppBrowser appBrowser;
	private HandlerManager eventBus;
	private FormPanel deployerForm;
		
	@UiField ProjectDeployerStyle style;
	@UiField DeckPanel deployerDeckPanel;
	
	public ProjectDeployer(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		this.deployerForm = new FormPanel();
		this.appBrowser = new AppBrowser(eventBus);
		this.projectOptions = new ProjectOptions(eventBus);
		this.databaseOptions = new DatabaseOptions(eventBus);
		this.deploymentOptions = new DeploymentOptions(eventBus);
		this.confirmBP = new ConfirmProject(deployerForm, eventBus);
		setupdeployerDeckPanel();
		registerEvents();
		setupBreadCrumbs();
		setupDeployerForm();
	}
	
	private void setupdeployerDeckPanel(){
		deployerDeckPanel.add(appBrowser);
		deployerDeckPanel.add(projectOptions);
		deployerDeckPanel.add(databaseOptions);
		deployerDeckPanel.add(deploymentOptions);
		//deployerDeckPanel.add(confirmBP);
		deployerDeckPanel.add(deployerForm);
		appBrowser.setTitle("Application Browser");
		projectOptions.setTitle("Project Options");
		databaseOptions.setTitle("Database Options");
		deploymentOptions.setTitle("Deployment Options");
		deployerDeckPanel.showWidget(0);
		appBrowser.setHeight("");
		appBrowser.setWidth("");
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {appBrowser.getTitle(), projectOptions.getTitle(), databaseOptions.getTitle(), deploymentOptions.getTitle()};
		eventBus.fireEvent(new BreadCrumbEvent("setCrumbs", crumbs));
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
					if( event.getTransitionType().equals("next") ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) + 1);
						eventBus.fireEvent(new BreadCrumbEvent("setActive", deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
						setFocus(panel);
					} else if( event.getTransitionType().equals("previous") ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) - 1);
						eventBus.fireEvent(new BreadCrumbEvent("setActive", deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
					}
				}
		});
	}
	
	public void setFocus(Widget panel){
		if( panel.getClass().equals(databaseOptions.getClass()) ){
			deploymentOptions.setFocus();
		} else if( panel.getClass().equals(appBrowser.getClass()) ){
			projectOptions.setFocus();
		} else if( panel.getClass().equals(projectOptions.getClass()) ){
			databaseOptions.setFocus();
		}
	}
	
	void handleConfirmBuildProjectLoad() {
		String username = projectOptions.usernameTextBox.getValue();
		String email = projectOptions.emailTextBox.getValue();
		
		String databaseEngine = databaseOptions.dbengineListBox.getItemText(databaseOptions.dbengineListBox.getSelectedIndex());
		String databaseName = databaseOptions.nameTextBox.getValue();
		String databasePassword = databaseOptions.passwordTextBox.getValue();
		String databaseHost = databaseOptions.hostTextBox.getValue();
		String databasePort = databaseOptions.portTextBox.getValue();
		
		String projectName = deploymentOptions.projectNameTextBox.getText() + deploymentOptions.baseProtocolLabel.getText();
		
		
		ArrayList<String> apps = appBrowser.getApps();
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
		  deployerForm.setAction(deploymentURL.replaceAll("projectName", deploymentOptions.projectNameTextBox.getText())); 
		  //createdProjectName = deploymentOptions.projectNameTextBox.getText();
		  
		  VerticalPanel formContainerPanel = new VerticalPanel();
		  this.deployerForm.add(formContainerPanel);
		  
		  ArrayList<String> paths = appBrowser.getAppPaths();
		  ArrayList<String> apptypes = appBrowser.getAppTypes();
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
	  
		  CheckBox debug = deploymentOptions.debugCheckBox;
		  formContainerPanel.add(debug);
		  
		  //Add all project options fields to the form for submission
		  formContainerPanel.add(projectOptions.projectOptionsPanel);
		  
		  //Add all database options fields to the form for submission
		  formContainerPanel.add(databaseOptions.databaseOptionsPanel);
		 
		  //Add all Database fields to the form for submissionsd
		  formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
			  deployerForm.submit();
	  }
}
