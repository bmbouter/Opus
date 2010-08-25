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

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ManagementConsole;
import opus.gwt.management.console.client.appbrowser.AppBrowserUiBinder;
import opus.gwt.management.console.client.dashboard.ProjectOptions;
import opus.gwt.management.console.client.resources.Deployer.DeployerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;


public class applicationDeployer extends Composite {
	private static applicationDeployerUiBinder uiBinder = GWT
		.create(applicationDeployerUiBinder.class);

	interface applicationDeployerUiBinder extends
		UiBinder<Widget, applicationDeployer> {}
		
	private final String deploymentURL =  "/deployments/projectName/";
		
	private ApplicationDetailDialog appInfoDialog = new ApplicationDetailDialog();
	private ProjectOptionsBuildProject projectOptions;
	//private AddAppsBuildProject addApps;
	private DatabaseOptions databaseOptions;
	private DeploymentOptionsBuildProject deploymentOptions;
	private ConfirmBuildProject confirmBP;

	private ProjectOptions projectSettings;
	
	private AppBrowserUiBinder appBrowser;
	
	private int navigationMenuFocusFlag;
	private String createdProjectName;
	private ManagementConsole managementCon;
	
	private Label activeLabel;
	private FormPanel deployerForm;
	private DeckPanel mainDeckPanel;
	private FlowPanel navigationMenuPanel;
	private Label titleBarLabel;
	private JSVariableHandler JSVarHandler;
		
	@UiField Label addAppsLabel;
	@UiField Label projectOptionsLabel;
	@UiField Label databaseOptionsLabel;
	@UiField Label deploymentOptionsLabel;
	@UiField Label confirmBPLabel;
	@UiField DeployerStyle style;
	
	public applicationDeployer(Label titleBarLabel, FlowPanel navigationMenuPanel, DeckPanel mainDeckPanel, ManagementConsole managementCon) {
		initWidget(uiBinder.createAndBindUi(this));
		this.managementCon = managementCon;
		createdProjectName = "";
		this.mainDeckPanel = mainDeckPanel;
		this.navigationMenuPanel = navigationMenuPanel;
		this.titleBarLabel = titleBarLabel;
		this.deployerForm = new FormPanel();
		this.appBrowser = new AppBrowserUiBinder(this,managementCon.getServerCommunicator());
		//this.addApps = new AddAppsBuildProject(this, managementCon.getServerCommunicator());
		this.projectOptions = new ProjectOptionsBuildProject(this);
		this.databaseOptions = new DatabaseOptions(this, managementCon.getServerCommunicator());
		//this.projectSettings = new ProjectOptions(managementCon.getServerCommunicator());
		this.deploymentOptions = new DeploymentOptionsBuildProject(this);
		this.confirmBP = new ConfirmBuildProject(deployerForm, this);
		this.activeLabel = addAppsLabel;
		this.navigationMenuFocusFlag = 0;
		activeLabel.setStyleName(style.navigationLabelActive());
		JSVarHandler = new JSVariableHandler();
		setupMainDeckPanel();
		setupNavigationMenuPanel();
		setupTitleBarLabel();
		setupDeployerForm();
	}
	
	private void setupMainDeckPanel(){
		//mainDeckPanel.add(projectSettings);
		mainDeckPanel.add(appBrowser);
		mainDeckPanel.add(projectOptions);
		mainDeckPanel.add(databaseOptions);
		mainDeckPanel.add(deploymentOptions);
		mainDeckPanel.add(confirmBP);
		mainDeckPanel.add(deployerForm);
		mainDeckPanel.showWidget(0);
		appBrowser.setHeight("");
		appBrowser.setWidth("");
	}
	
	private void setupNavigationMenuPanel(){
		navigationMenuPanel.add(addAppsLabel);
		navigationMenuPanel.add(projectOptionsLabel);
		navigationMenuPanel.add(databaseOptionsLabel);
		navigationMenuPanel.add(deploymentOptionsLabel);
		navigationMenuPanel.add(confirmBPLabel);
	}
	
	private void setupTitleBarLabel(){
		titleBarLabel.setText("Deploy New Project");
	}
	
	private void setupDeployerForm(){
		 deployerForm.setMethod(FormPanel.METHOD_POST);
		  deployerForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        managementCon.onDeployNewProject(createdProjectName);
		      }
		    });
	}
	
	 void handleAddAppsLabel(){
		  if(navigationMenuFocusFlag != 0){
			  addAppsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(0);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = addAppsLabel;
			  navigationMenuFocusFlag = 0;
		  }
	  }
	  
	 public void handleProjectOptionsLabel(){
		  if(navigationMenuFocusFlag != 1){
			  projectOptionsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(1);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = projectOptionsLabel;
			  navigationMenuFocusFlag = 1;
		  }
	  }
	  
	  void handleDatabaseOptionsLabel(){
		  if(navigationMenuFocusFlag != 2){
			  databaseOptionsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(2);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = databaseOptionsLabel;
			  navigationMenuFocusFlag = 2;
		  }
	  }
	  
	  void handleDeploymentOptionsLabel(){
		  if(navigationMenuFocusFlag != 3){
			  deploymentOptionsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(3);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = deploymentOptionsLabel;
			  navigationMenuFocusFlag = 3;
		  }
	  }
	  
	  void handleConfirmBPLabel(){
		  if(navigationMenuFocusFlag != 4){
			  confirmBPLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(4);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = confirmBPLabel;
			  navigationMenuFocusFlag = 4;
		  }
	  }
	  
	  void handleConfirmBuildProjectLoad() {
			
			
			String username = projectOptions.usernameTextBox.getValue();
			String email = projectOptions.emailTextBox.getValue();
			Boolean admin = projectOptions.adminCheckBox.getValue();
			
			String databaseEngine = databaseOptions.dbengineListBox.getItemText(databaseOptions.dbengineListBox.getSelectedIndex());
			String databaseName = databaseOptions.nameTextBox.getValue();
			String databasePassword = databaseOptions.passwordTextBox.getValue();
			String databaseHost = databaseOptions.hostTextBox.getValue();
			String databasePort = databaseOptions.portTextBox.getValue();
			
			String projectName = deploymentOptions.projectNameTextBox.getText() + deploymentOptions.baseUrlLabel.getText();
			
			
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

			if (admin == true) {
				html += "Yes</p>";
			} else {
				html += "No</p>";
			}
			
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
		  deployerForm.setAction(JSVarHandler.getDeployerBaseURL() + deploymentURL.replaceAll("projectName", deploymentOptions.projectNameTextBox.getText())); 
		  createdProjectName = deploymentOptions.projectNameTextBox.getText();
		  
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
			  RadioButton pathtype = new RadioButton("form-" + i + "-apptype");
			  pathtype.setFormValue(apptypes.get(i));
			  pathtype.setValue(true);
			  TextBox path = new TextBox();
			  path.setName("form-" + i +"-apppath");
			  path.setValue(paths.get(i));
			  formContainerPanel.add(pathtype);
			  formContainerPanel.add(path);
		  }
		  
		  //Add all project options fields to the form for submission
		  formContainerPanel.add(projectOptions.projectOptionsPanel);
		  
		  //Add all database options fields to the form for submission
		  formContainerPanel.add(databaseOptions.databaseOptionsPanel);
		 
		  //Add all Database fields to the form for submissionsd
		  formContainerPanel.add(deploymentOptions.activeCheckBox);
		  formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
		  deployerForm.submit();
	  }

	  ProjectOptionsBuildProject getProjectOptions() {
		  return projectOptions;
	  }
	  /*
	  AddAppsBuildProject getAddApps() {
		  return addApps;
	  }
	  */
	  DatabaseOptions getDatabaseOptions(){
		  return databaseOptions;
	  }
	  
	  DeploymentOptionsBuildProject getDeploymentOptions(){
		  return deploymentOptions;
	  }
	  
	  public native String getBaseURL()/*-{
	  	return $wnd.baseURL;
	  }-*/;
}
