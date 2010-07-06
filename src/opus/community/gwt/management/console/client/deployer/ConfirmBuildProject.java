package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class ConfirmBuildProject extends Composite {

	private static ConfirmBuildProjectUiBinder uiBinder = GWT
			.create(ConfirmBuildProjectUiBinder.class);

	interface ConfirmBuildProjectUiBinder extends
			UiBinder<Widget, ConfirmBuildProject> {
	}

	private FormPanel deployerForm;
	private applicationDeployer appDeployer;
	
	@UiField ScrollPanel confirmationScrollPanel;
	@UiField Button previousButton;
	
	public ConfirmBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
/*		confirmationScrollPanel.add(deployerForm);
		AddAppsBuildProject addApps = appDeployer.getAddApps();
		ProjectOptionsBuildProject projectOptions = appDeployer.getProjectOptions();
		DatabaseOptionsBuildProject databaseOptions = appDeployer.getDatabaseOptions();
		DeploymentOptionsBuildProject deploymentOptions = appDeployer.getDeploymentOptions();
		
		String username = projectOptions.usernameTextBox.getValue();
		String email = projectOptions.emailTextBox.getValue();
		Boolean admin = projectOptions.adminCheckBox.getValue();
		
		String database = databaseOptions.dbengineListBox.getItemText(databaseOptions.dbengineListBox.getSelectedIndex());
		databaseOptions.nameTextBox.getValue();
		//databaseOptions.
*/		
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleDeploymentOptionsLabel();
	}
	
	@UiHandler("confirmButton")
	void handleConfirmButton(ClickEvent event){
		appDeployer.handleConfirmDeployProject();
	}
}
