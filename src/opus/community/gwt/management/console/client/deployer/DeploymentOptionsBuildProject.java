package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
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
	
	public DeploymentOptionsBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
		baseUrlLabel.setText(appDeployer.getBaseURL());
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		appDeployer.handleConfirmBPLabel();
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleDatabaseOptionsLabel();
	}
}
