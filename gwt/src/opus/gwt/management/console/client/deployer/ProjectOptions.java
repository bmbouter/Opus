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
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class ProjectOptions extends Composite {

	private static BuildProjectPage2UiBinder uiBinder = GWT.create(BuildProjectPage2UiBinder.class);
	interface BuildProjectPage2UiBinder extends UiBinder<Widget, ProjectOptions> {}
	
	private ProjectDeployer projectDeployer;
	
	@UiField TextBox usernameTextBox;
	@UiField TextBox emailTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField PasswordTextBox passwordConfirmTextBox;
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField HTMLPanel projectOptionsPanel;
	@UiField ListBox idProvider;
	
	
	public ProjectOptions(ProjectDeployer projectDeployer) {
		initWidget(uiBinder.createAndBindUi(this));
		this.projectDeployer = projectDeployer;
	}	

	public void setAllowedAuthApps(String allowedAuthApps){
		int size = idProvider.getItemCount();
		for(int i=0; i < size; i++){
			idProvider.removeItem(0);
		}
		String[] options = allowedAuthApps.split(",");
		for(String option : options){
			idProvider.addItem(option, option);
		}
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			//projectDeployer.handleDatabaseOptionsLabel();
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		//projectDeployer.handleAddAppsLabel();
	}
	
	public boolean validateFields(){
		if( !usernameTextBox.getText().isEmpty() ){
			if(passwordTextBox.getText().isEmpty()){
				Window.alert("Password required to create Superuser");
				return false;
			} 
			if(emailTextBox.getText().isEmpty()){
				Window.alert("Superuser Email required to create Superuser.");
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
