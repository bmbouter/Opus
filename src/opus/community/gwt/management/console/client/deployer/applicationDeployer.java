package opus.community.gwt.management.console.client.deployer;

import java.util.ArrayList;
import java.util.List;

import opus.community.gwt.management.console.client.resources.Deployer.DeployerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.DisclosurePanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;


public class applicationDeployer extends Composite {
		
	private ApplicationDetailDialog appInfoDialog = new ApplicationDetailDialog();
	private ProjectOptionsBuildProject projectOptions;
	private AddAppsBuildProject addApps;
	private DatabaseOptionsBuildProject databaseOptions;
	private DeploymentOptionsBuildProject deploymentOptions;
	private ConfirmBuildProject confirmBP;

	private static applicationDeployerUiBinder uiBinder = GWT
			.create(applicationDeployerUiBinder.class);
		
	interface applicationDeployerUiBinder extends
			UiBinder<Widget, applicationDeployer> {}

	private Label activeLabel;
	private int navigationMenuFocusFlag;
	private FormPanel deployerForm;
		
	@UiField Label addAppsLabel;
	@UiField Label projectOptionsLabel;
	@UiField Label databaseOptionsLabel;
	@UiField Label deploymentOptionsLabel;
	@UiField Label confirmBPLabel;
	@UiField DeckPanel mainDeckPanel;
	@UiField DeployerStyle style;
	
	public applicationDeployer() {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = new FormPanel();
		this.projectOptions = new ProjectOptionsBuildProject(deployerForm, this);
		this.databaseOptions = new DatabaseOptionsBuildProject(deployerForm, this);
		this.deploymentOptions = new DeploymentOptionsBuildProject(deployerForm, this);
		this.confirmBP = new ConfirmBuildProject(deployerForm, this);
		this.activeLabel = addAppsLabel;
		this.projectOptions =  new ProjectOptionsBuildProject(deployerForm, this);
		this.addApps = new AddAppsBuildProject(this,this.deployerForm);
		mainDeckPanel.add(addApps);
		mainDeckPanel.add(projectOptions);
		mainDeckPanel.add(databaseOptions);
		mainDeckPanel.add(deploymentOptions);
		mainDeckPanel.add(confirmBP);
		this.navigationMenuFocusFlag = 0;
		mainDeckPanel.showWidget(0);
		activeLabel.setStyleName(style.navigationLabelActive());
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
	  
	  void handleProjectOptionsLabel(){
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

	  ProjectOptionsBuildProject getProjectOptions() {
		  return projectOptions;
	  }
	  
	  AddAppsBuildProject getAddApps() {
		  return addApps;
	  }
	  
	  DatabaseOptionsBuildProject getDatabaseOptions(){
		  return databaseOptions;
	  }
	  
	  DeploymentOptionsBuildProject getDeploymentOptions(){
		  return deploymentOptions;
	  }
	  
	  public native String getBaseURL()/*-{

	  return $wnd.baseURL;

	  }-*/;
}
