package opus.community.gwt.management.console.client.deployer;

import java.util.HashMap;

import opus.community.gwt.management.console.client.JSVariableHandler;
import opus.community.gwt.management.console.client.ServerCommunicator;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockLayoutPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DatabaseOptionsBuildProject extends Composite {

	private static DatabaseOptionsBuildProjectUiBinder uiBinder = GWT
			.create(DatabaseOptionsBuildProjectUiBinder.class);
	
	interface DatabaseOptionsBuildProjectUiBinder extends
			UiBinder<Widget, DatabaseOptionsBuildProject> {
	}

	final String dbOptionsURL = "";
	
	private applicationDeployer appDeployer;
	private HashMap<String, String> dbOptions;
	private boolean optionsFlag;
	private JSVariableHandler JSVarHandler;
	private ServerCommunicator serverComm;

	@UiField DockLayoutPanel dboptionsPanel;
	@UiField TextBox nameTextBox;
	@UiField TextBox passwordTextBox;
	@UiField TextBox hostTextBox;
	@UiField TextBox portTextBox;
	@UiField ListBox dbengineListBox;
	@UiField Button nextButton;
	@UiField Button previousButton;	
	@UiField DockLayoutPanel databaseOptionsPanel;
	
	public DatabaseOptionsBuildProject(applicationDeployer appDeployer, ServerCommunicator serverComm) {
		initWidget(uiBinder.createAndBindUi(this));
		JSVarHandler = new JSVariableHandler();
		this.serverComm = serverComm;
		this.appDeployer = appDeployer;
		dbOptions = new HashMap<String, String>();
		checkForDBOptions();
	}
	
	private void checkForDBOptions(){
		if( dbOptionsURL.equals("")){
			optionsFlag = true;
			setupDBOptions();
		} else {
			final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + dbOptionsURL);
			serverComm.getJson(url, serverComm, 8, this);
		}
	}
	
	private void setupDBOptions(){
		if( optionsFlag ){
			dbOptions.put("Sqlite3", "sqlite3");
			dbOptions.put("Postgresql", "postgresql_psycopg2");
			dbOptions.put("Mysql", "mysql");
			dbOptions.put("Oracle", "oracle");
		}
		for(String key : dbOptions.keySet()){
			if( key == "Sqlite3" ){
				dbengineListBox.insertItem(key, dbOptions.get(key), 0);
				dbengineListBox.setSelectedIndex(0);
			} else {
				dbengineListBox.addItem(key, dbOptions.get(key));
			}
		}
		setDBOptionParams();
	}
	
	private void setDBOptionParams(){
		String item = dbengineListBox.getItemText(dbengineListBox.getSelectedIndex());
		if( item.equals("Sqlite3") ){
			dboptionsPanel.setVisible(false);
		} else {
			dboptionsPanel.setVisible(true);
		}	
	}
	
	@UiHandler("dbengineListBox")
	void handleDBEngineListBox(ChangeEvent event){
		setDBOptionParams();	
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
	
	public void handleDBOptions(JsArray<DBOptionsData> dbOptionsData){
		if(dbOptionsData.length() == 0){
			optionsFlag = true;
			setupDBOptions();
		}
	}

	public final native JsArray<DBOptionsData> asArrayOfDBOptionsData(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}

	