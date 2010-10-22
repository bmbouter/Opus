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

import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.UpdateDBOptionsEvent;
import opus.gwt.management.console.client.event.UpdateDBOptionsEventHandler;
import opus.gwt.management.console.client.overlays.DBOptions;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.KeyUpEvent;
import opus.gwt.management.console.client.ClientFactory;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DatabaseOptionsPanel extends Composite {

	private static DatabaseOptionsUiBinder uiBinder = GWT.create(DatabaseOptionsUiBinder.class);
	interface DatabaseOptionsUiBinder extends UiBinder<Widget, DatabaseOptionsPanel> {}
	
	private HashMap<String, String> dbOptions;
	private boolean optionsFlag;
	private boolean postgresAutoConfig;
	private EventBus eventBus;
	
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
	@UiField ProjectDeployerStyle deployer;
	
	public DatabaseOptionsPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = clientFactory.getEventBus();
		postgresAutoConfig = false;
		dbOptions = new HashMap<String, String>();
		registerHandlers();
		checkForDBOptions();
		setTooltipInitialState();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(UpdateDBOptionsEvent.TYPE, 
			new UpdateDBOptionsEventHandler(){
				public void onUpdateDBOptions(UpdateDBOptionsEvent event){
					handleDBOptions(event.getDBOptionsData());
				}
		});
	}
	
	public void handleDBOptions(DBOptions dbOptionsData){
		optionsFlag = false;
		
		String[] options = dbOptionsData.getAllowedDatabases().split(",");
		
		for(String option : options){
			dbOptions.put(option, option);
		}
		postgresAutoConfig = dbOptionsData.getAutoPostgresConfig();
		setupDBOptions();
	}
	
	private void checkForDBOptions(){
		eventBus.fireEvent(new AsyncRequestEvent("handleDBOptions"));
	}
	
	private void setupDBOptions(){
		if( optionsFlag ){
			dbOptions.put("sqlite3", "sqlite3");
			dbOptions.put("postgresql", "postgresql_psycopg2");
			dbOptions.put("mysql", "mysql");
			dbOptions.put("oracle", "oracle");
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
	
	public String getPostData(){
		StringBuffer postData = new StringBuffer();
		postData.append("&dbengine=");
		postData.append( URL.encodeQueryString(dbengineListBox.getValue(dbengineListBox.getSelectedIndex())));
		postData.append("&dbname=");
		postData.append( URL.encodeQueryString(nameTextBox.getValue()));
		postData.append("&dbpassword=");
		postData.append( URL.encodeQueryString(passwordTextBox.getValue()));
		postData.append("&dbhost=");
		postData.append( URL.encodeQueryString(hostTextBox.getValue()));
		postData.append("&dbport=");
		postData.append( URL.encodeQueryString(portTextBox.getValue()));
		return postData.toString();
	}
	
	@UiHandler("dbengineListBox")
	void handleDBEngineListBox(ChangeEvent event){
		setDBOptionParams();	
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		//if(validateFields()){
			eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.NEXT, this));
		//}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.PREVIOUS, this));
	}
	
	@UiHandler("nameTextBox")
	void handleNameTextBoxOnFocus(FocusEvent event) {
		active.setVisible(true);
	
		int x = getTooltipPosition(nameTextBox)[0];
		int y = getTooltipPosition(nameTextBox)[1];
		
		setTooltipPosition(x, y);
		
		setTooltipText("Enter the database username.");
	}
	
	@UiHandler("passwordTextBox")
	void handlePasswordTextBoxOnFocus(FocusEvent event) {
		int x = getTooltipPosition(passwordTextBox)[0];
		int y = getTooltipPosition(passwordTextBox)[1];
		
		setTooltipPosition(x, y);
		
		setTooltipText("Enter the password for the user.");
	}
	
	@UiHandler("hostTextBox")
	void handleHostTextBoxOnFocus(FocusEvent event) {
		int x = getTooltipPosition(hostTextBox)[0];
		int y = getTooltipPosition(hostTextBox)[1];
		
		setTooltipPosition(x, y);
		
		setTooltipText("Enter the host for the database.");
	}
	
	@UiHandler("portTextBox")
	void handlePortTextBoxOnFocus(FocusEvent event) {
		int x = getTooltipPosition(portTextBox)[0];
		int y = getTooltipPosition(portTextBox)[1];
		
		setTooltipPosition(x, y);
		
		setTooltipText("Enter the port for the database.");
	}
	
	@UiHandler("nameTextBox")
	void handleNameTextBoxOnChange(KeyUpEvent event) {
		nameTextBox.removeStyleName(deployer.redBorder());
	}
	
	@UiHandler("passwordTextBox")
	void handlePasswordTextBoxOnChange(KeyUpEvent event) {
		passwordTextBox.removeStyleName(deployer.redBorder());
	}
	
	@UiHandler("hostTextBox")
	void handleHostTextBoxOnChange(KeyUpEvent event) {
		hostTextBox.removeStyleName(deployer.redBorder());
	}
	
	@UiHandler("portTextBox")
	void handlePortTextBoxOnChange(KeyUpEvent event) {
		portTextBox.removeStyleName(deployer.redBorder());
	}
	
	private boolean validateFields(){
		if(!dbengineListBox.isItemSelected(0)){
			if(nameTextBox.getText().isEmpty() 
					|| passwordTextBox.getText().isEmpty() 
					|| hostTextBox.getText().isEmpty()
					|| portTextBox.getText().isEmpty()) {
				highlightFields();
				Window.alert("All fields must be filled out.");
				return false;
			} else {
				return true;
			}
		} else {
			return true;
		}
	}
	
	/**
	 * Highlight fields that are incorrect
	 */
	private void highlightFields() {
		if(nameTextBox.getText().isEmpty()) {
			nameTextBox.setStyleName(deployer.redBorder());
		}
		
		if(passwordTextBox.getText().isEmpty()) {
			passwordTextBox.setStyleName(deployer.redBorder());
		}
		
		if(hostTextBox.getText().isEmpty()) {
			hostTextBox.setStyleName(deployer.redBorder());
		}
		
		if(portTextBox.getText().isEmpty()) {
			portTextBox.setStyleName(deployer.redBorder());
		}
	}
	
	/**
	 * Set the tooltips initial state on page load
	 */
	private void setTooltipInitialState() {
		active.setVisible(false);
	}
	
	/**
	 * Set the position of a tooltip relative to the browser window
	 * @param x the x coordinate
	 * @param y the y coordinate
	 */
	private void setTooltipPosition(int x, int y) {
		active.setPopupPosition(x, y);
	}
	
	/**
	 * Set the text of a tooltip
	 * @param text the text to set
	 */
	private void setTooltipText(String text) {
		active.hide();
		active.setText(text);
		active.show();
	}
	
	/**
	 * Return the tooltip position as an array in for them [x, y]
	 * @param textbox the textbox to get the position of
	 * @return tooltip position
	 */
	private int[] getTooltipPosition(TextBox textbox) {
		int[] pos = new int[2];
		
		pos[0] = textbox.getAbsoluteLeft() + textbox.getOffsetWidth() + 5;
		pos[1] = textbox.getAbsoluteTop() + 2;
		
		return pos;
	}
	
	/**
	 * Return the tooltip position as an array in for them [x, y]
	 * @param textbox the textbox to get the position of
	 * @return tooltip position
	 */
	private int[] getTooltipPosition(PasswordTextBox textbox) {
		int[] pos = new int[2];
		
		pos[0] = textbox.getAbsoluteLeft() + textbox.getOffsetWidth() + 5;
		pos[1] = textbox.getAbsoluteTop() + 2;
		
		return pos;
	}
}

	