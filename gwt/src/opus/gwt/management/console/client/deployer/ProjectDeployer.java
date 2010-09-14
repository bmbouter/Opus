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
import java.util.HashMap;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.PanelManager;
import opus.gwt.management.console.client.dashboard.ProjectSettings;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;

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


public class ProjectDeployer extends Composite {
	private static applicationDeployerUiBinder uiBinder = GWT
		.create(applicationDeployerUiBinder.class);

	interface applicationDeployerUiBinder extends
		UiBinder<Widget, ProjectDeployer> {}
		
	private final String deploymentURL =  "/deployments/projectName/";
		
	private ApplicationPopup appInfoDialog = new ApplicationPopup(); 
	private ProjectOptions projectOptions;
	private DatabaseOptions databaseOptions;
	private DeploymentOptions deploymentOptions;
	private ConfirmProject confirmBP;
	private HashMap<String, Integer> childPanels;

	private ProjectSettings projectSettings;
	
	private AppBrowser appBrowser;
	
	private int navigationMenuFocusFlag;
	private String createdProjectName;
	private PanelManager panelManager;
	
	private FormPanel deployerForm;
	private FlowPanel navigationMenuPanel;
	private Label titleBarLabel;
	private JSVariableHandler JSVarHandler;
		
	@UiField ProjectDeployerStyle style;
	@UiField DeckPanel deployerDeckPanel;
	
	public ProjectDeployer(PanelManager panelManager) {
		initWidget(uiBinder.createAndBindUi(this));
		childPanels = new HashMap<String, Integer>();
		this.panelManager = panelManager;
		createdProjectName = "";
		this.deployerForm = new FormPanel();
		this.appBrowser = new AppBrowser(this, panelManager.getServerCommunicator());
		this.projectOptions = new ProjectOptions(this);
		this.databaseOptions = new DatabaseOptions(this, panelManager.getServerCommunicator());
		this.deploymentOptions = new DeploymentOptions(this);
		this.confirmBP = new ConfirmProject(deployerForm, this);
		this.navigationMenuFocusFlag = 0;
		JSVarHandler = new JSVariableHandler();
		setupdeployerDeckPanel();
		setupDeployerForm();
	}
	
	private void setupdeployerDeckPanel(){
		//deployerDeckPanel.add(projectSettings);
		deployerDeckPanel.add(appBrowser);
		deployerDeckPanel.add(projectOptions);
		deployerDeckPanel.add(databaseOptions);
		deployerDeckPanel.add(deploymentOptions);
		deployerDeckPanel.add(confirmBP);
		deployerDeckPanel.add(deployerForm);
		deployerDeckPanel.showWidget(1);
		appBrowser.setHeight("");
		appBrowser.setWidth("");
	}
	
	private void setupDeployerForm(){
		 deployerForm.setMethod(FormPanel.METHOD_POST);
		  deployerForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        panelManager.onDeployNewProject(createdProjectName);
		      }
		    });
	}
	
	public void showNextPanel(Object panel){
		deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex((Widget) panel) + 1);
	}

	public void showPreviousPanel(Object panel){
		deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex((Widget) panel) - 1);
	}
	
	  void handleConfirmBuildProjectLoad() {
			
			
			String username = projectOptions.usernameTextBox.getValue();
			String email = projectOptions.emailTextBox.getValue();
			
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
	  
		  //Add all project options fields to the form for submission
		  formContainerPanel.add(projectOptions.projectOptionsPanel);
		  
		  //Add all database options fields to the form for submission
		  formContainerPanel.add(databaseOptions.databaseOptionsPanel);
		 
		  //Add all Database fields to the form for submissionsd
		  formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
			  deployerForm.submit();
	  }
	
	  public ProjectOptions getProjectOptions() {
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
	  
	  DeploymentOptions getDeploymentOptions(){
		  return deploymentOptions;
	  }
	  
	  public native String getBaseURL()/*-{
	  	return $wnd.baseURL;
	  }-*/;
}
