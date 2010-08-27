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

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockLayoutPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class ProjectOptions extends Composite {

	private static BuildProjectPage2UiBinder uiBinder = GWT
			.create(BuildProjectPage2UiBinder.class);

	interface BuildProjectPage2UiBinder extends
			UiBinder<Widget, ProjectOptions> {
	}
	
	private applicationDeployer appDeployer;
	
	@UiField TextBox usernameTextBox;
	@UiField TextBox emailTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField PasswordTextBox passwordConfirmTextBox;
	@UiField CheckBox adminCheckBox;
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField DockLayoutPanel projectOptionsPanel;
	@UiField ListBox idProvider;
	
	public ProjectOptions(applicationDeployer appDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.appDeployer = appDeployer;
		idProvider.addItem("");
		idProvider.addItem("Local","local");
		idProvider.addItem("LDAP","ldap");
		idProvider.addItem("OpenId","openid");
	}	

	public void setAllowedAuthApps(String allowedAuthApps){
		int size = idProvider.getItemCount();
		for(int i=0; i < size; i++){
			idProvider.removeItem(0);
		}
		String[] options = allowedAuthApps.split(",");
		idProvider.addItem("");
		for(String option : options){
			idProvider.addItem(option, option);
		}
	}
	
	@UiHandler("idProvider")
	void handleChangeIdProvider(ChangeEvent event){
		if(idProvider.getItemText(idProvider.getSelectedIndex()).equals("Local")){
			adminCheckBox.setValue(true);
			adminCheckBox.setEnabled(false);
		} else {
			adminCheckBox.setEnabled(true);			
		}
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
