package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockLayoutPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DatabaseOptionsBuildProject extends Composite {

	private static DatabaseOptionsBuildProjectUiBinder uiBinder = GWT
			.create(DatabaseOptionsBuildProjectUiBinder.class);
	
	interface DatabaseOptionsBuildProjectUiBinder extends
			UiBinder<Widget, DatabaseOptionsBuildProject> {
	}

	private FormPanel deployerForm;
	private applicationDeployer appDeployer;

	@UiField DockLayoutPanel dboptionsPanel;
	@UiField TextBox nameTextBox;
	@UiField TextBox passwordTextBox;
	@UiField TextBox hostTextBox;
	@UiField TextBox portTextBox;
	@UiField ListBox dbengineListBox;
	@UiField Button nextButton;
	@UiField Button previousButton;	
	@UiField DockLayoutPanel databaseOptionsPanel;
	
	public DatabaseOptionsBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
		this.dbengineListBox.addItem("Sqlite3", "sqlite3");
		this.dbengineListBox.addItem("Postgresql", "postgresql_psycopg2");
		this.dbengineListBox.addItem("Mysql", "mysql");
		this.dbengineListBox.addItem("Oracle", "oracle");
		setDBOptionParams();
	}
	
	@UiHandler("dbengineListBox")
	void handleDBEngineListBox(ChangeEvent event){
		setDBOptionParams();	
	}
	
	private void setDBOptionParams(){
		int index = dbengineListBox.getSelectedIndex();
		if(index == 0){
			dboptionsPanel.setVisible(false);
		} else {
			dboptionsPanel.setVisible(true);
		}	
	}
		
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			appDeployer.handleDeploymentOptionsLabel();
		}
		
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleProjectOptionsLabel();
	}
	
	private boolean validateFields(){
		if(!dbengineListBox.isItemSelected(0)){
			if(nameTextBox.getText().isEmpty() 
					|| passwordTextBox.getText().isEmpty() 
					|| hostTextBox.getText().isEmpty()
					|| portTextBox.getText().isEmpty()){
				Window.alert("All fields must be filled out.");
				return false;
			} else {
				return true;
			}
		} else {
			return true;
		}
	}
}

	