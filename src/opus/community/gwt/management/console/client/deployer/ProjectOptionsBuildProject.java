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
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class ProjectOptionsBuildProject extends Composite {

	private static BuildProjectPage2UiBinder uiBinder = GWT
			.create(BuildProjectPage2UiBinder.class);

	interface BuildProjectPage2UiBinder extends
			UiBinder<Widget, ProjectOptionsBuildProject> {
	}
	
	private FormPanel deployerForm;
	private applicationDeployer appDeployer;
	
	@UiField TextBox usernameTextBox;
	@UiField TextBox emailTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField PasswordTextBox passwordConfirmTextBox;
	@UiField CheckBox adminCheckBox;
	@UiField Button nextButton;
	@UiField Button previousButton;
	
	public ProjectOptionsBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
	}	
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			appDeployer.handleDatabaseOptionsLabel();
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleAddAppsLabel();
	}
	
	public boolean validateFields(){
		if(!usernameTextBox.getText().isEmpty()){
			if(passwordTextBox.getText().isEmpty()){
				Window.alert("Password required to create Superuser");
				return false;
			} 
			if(emailTextBox.getText().isEmpty()){
				Window.alert("Superuser Email required to create Superuser.");
				return false;
			}
		}
		if(adminCheckBox.getValue()){
			if(usernameTextBox.getText().isEmpty() || passwordTextBox.getText().isEmpty() || emailTextBox.getText().isEmpty()){
				Window.alert("Django Admin Interface requires the creation of a superuser.");
				return false;
			}
		}
		if(!passwordTextBox.getText().equals(passwordConfirmTextBox.getText())){
			Window.alert("Passwords do not match");
			return false;
		}
		return true;
	}
}
