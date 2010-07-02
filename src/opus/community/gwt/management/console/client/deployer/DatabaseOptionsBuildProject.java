package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockLayoutPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
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
	@UiField ListBox dbengineListBox;
	@UiField Button nextButton;
	@UiField Button previousButton;	

	public DatabaseOptionsBuildProject(FormPanel deployerForm, applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.appDeployer = appDeployer;
		this.dbengineListBox.addItem("postgresql_psycopg2");
		this.dbengineListBox.addItem("mysql");
		this.dbengineListBox.addItem("oracle");
		this.dbengineListBox.addItem("sqlite3");
	}
	
	@UiHandler("dbengineListBox")
	void handleDBEngineListBox(ChangeEvent event){
		int index = dbengineListBox.getSelectedIndex();
		if(index == 3){
			dboptionsPanel.setVisible(false);
		} else {
			dboptionsPanel.setVisible(true);
		}
	}
		
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		appDeployer.handleDeploymentOptionsLabel();
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		appDeployer.handleProjectOptionsLabel();
	}
}

	