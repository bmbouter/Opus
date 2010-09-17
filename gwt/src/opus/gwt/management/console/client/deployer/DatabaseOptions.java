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

import java.util.HashMap;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ServerCommunicator;
import opus.gwt.management.console.client.overlays.DatabaseOptionsData;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DatabaseOptions extends Composite {

	private static DatabaseOptionsUiBinder uiBinder = GWT.create(DatabaseOptionsUiBinder.class);
	interface DatabaseOptionsUiBinder extends UiBinder<Widget, DatabaseOptions> {}

	final String dbOptionsURL = "/json/database/?callback=";
	
	private ProjectDeployer projectDeployer;
	private HashMap<String, String> dbOptions;
	private boolean optionsFlag;
	private JSVariableHandler JSVarHandler;
	private ServerCommunicator serverComm;
	private boolean postgresAutoConfig;
	
	@UiField HTMLPanel dbFieldsPanel;
	@UiField TextBox nameTextBox;
	@UiField TextBox passwordTextBox;
	@UiField TextBox hostTextBox;
	@UiField TextBox portTextBox;
	@UiField ListBox dbengineListBox;
	@UiField Button nextButton;
	@UiField Button previousButton;	
	@UiField HTMLPanel databaseOptionsPanel;
	@UiField TooltipPanel active;
	
	public DatabaseOptions(ProjectDeployer projectDeployer, ServerCommunicator serverComm) {
		initWidget(uiBinder.createAndBindUi(this));
		JSVarHandler = new JSVariableHandler();
		postgresAutoConfig = false;
		this.serverComm = serverComm;
		this.projectDeployer = projectDeployer;
		dbOptions = new HashMap<String, String>();
		checkForDBOptions();
		setTooltipInitialState();
	}
	
	private void checkForDBOptions(){
		if( dbOptionsURL.equals("")){
			optionsFlag = true;
			setupDBOptions();
		} else {
			final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + dbOptionsURL);
			serverComm.getJson(url, serverComm, "handleDBOptions", this);
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
			if( key == "sqlite3" ){
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
		if( item.equals("sqlite3") ){
			dbFieldsPanel.setVisible(false);
		} else if( postgresAutoConfig && item.equals("postgresql_psycopg2") ) {
			dbFieldsPanel.setVisible(false);
		} else {
			dbFieldsPanel.setVisible(true);
		}	
	}
	
	public void setFocus(){
		dbengineListBox.setFocus(true);
	}
	
	@UiHandler("dbengineListBox")
	void handleDBEngineListBox(ChangeEvent event){
		setDBOptionParams();	
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			projectDeployer.showNextPanel(this);
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		projectDeployer.showPreviousPanel(this);
	}
	
	@UiHandler("nameTextBox")
	void handleNameTextBoxOnFocus(FocusEvent event) {
		active.setVisible(true);
	
		int x = nameTextBox.getAbsoluteLeft() + nameTextBox.getOffsetWidth() + 5;
		int y = nameTextBox.getAbsoluteTop() + 2;
		
		setTooltipPosition(x, y);
		
		active.hide();
		active.setText("This is where the name stuff goes!");
		active.show();
	}
	
	@UiHandler("passwordTextBox")
	void handlePasswordTextBoxOnFocus(FocusEvent event) {
		int x = passwordTextBox.getAbsoluteLeft() + passwordTextBox.getOffsetWidth() + 5;
		int y = passwordTextBox.getAbsoluteTop() + 2;
		
		setTooltipPosition(x, y);
		
		active.hide();
		active.setText("This is where the password stuff goes!");
		active.show();
	}
	
	@UiHandler("hostTextBox")
	void handleHostTextBoxOnFocus(FocusEvent event) {
		int x = hostTextBox.getAbsoluteLeft() + hostTextBox.getOffsetWidth() + 5;
		int y = hostTextBox.getAbsoluteTop() + 2;
		
		setTooltipPosition(x, y);
		
		active.hide();
		active.setText("This is where the host stuff goes!");
		active.show();
	}
	
	@UiHandler("portTextBox")
	void handlePortTextBoxOnFocus(FocusEvent event) {
		int x = portTextBox.getAbsoluteLeft() + portTextBox.getOffsetWidth() + 5;
		int y = portTextBox.getAbsoluteTop() + 2;
		
		setTooltipPosition(x, y);
		
		active.hide();
		active.setText("This is where the port stuff goes!");
		active.show();
	}
	
	private boolean validateFields(){
		//TODO: REMOVE THIS LATER
		dbengineListBox.insertItem("Test", 0);
		
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
	
	public void handleDBOptions(DatabaseOptionsData dbOptionsData){
		optionsFlag = false;
		
		String[] options = dbOptionsData.getAllowedDatabases().split(",");
		
		for(String option : options){
			dbOptions.put(option, option);
		}
		postgresAutoConfig = dbOptionsData.getAutoPostgresConfig();
		projectDeployer.getProjectOptions().setAllowedAuthApps(dbOptionsData.getAllowedAuthApps());
		setupDBOptions();
	}
	
	private void setTooltipInitialState() {
		active.setVisible(false);
	}
	
	private void setTooltipPosition(int x, int y) {
		active.setPopupPosition(x, y);
	}
}

	