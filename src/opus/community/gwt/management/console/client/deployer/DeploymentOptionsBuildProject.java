package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DeploymentOptionsBuildProject extends Composite {

	private static DeploymentOptionsBuildProjectUiBinder uiBinder = GWT
			.create(DeploymentOptionsBuildProjectUiBinder.class);

	interface DeploymentOptionsBuildProjectUiBinder extends
			UiBinder<Widget, DeploymentOptionsBuildProject> {
	}

	private FormPanel deployerForm;
	private applicationDeployer appDeployer;
	
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField Label baseUrlLabel;
	@UiField TextBox projectNameTextBox;
	@UiField CheckBox activeCheckBox;
	@UiField ScrollPanel deploymentOptionsScrollPanel;

	public DeploymentOptionsBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
		baseUrlLabel.setText(appDeployer.getBaseURL());
		activeCheckBox.setValue(true);
		projectNameTextBox.setFocus(true);
	}
	
	private boolean validateFields(){
		if(projectNameTextBox.getText().isEmpty()){
			Window.alert("Subdomain required to deploy");
			return false;
		} else {
			return true;
		}
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			appDeployer.handleConfirmBPLabel();
			appDeployer.handleConfirmBuildProjectLoad();
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleDatabaseOptionsLabel();
	}
}
