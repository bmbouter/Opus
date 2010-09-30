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

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DeploymentOptions extends Composite {

	private static DeploymentOptionsBuildProjectUiBinder uiBinder = GWT.create(DeploymentOptionsBuildProjectUiBinder.class);
	interface DeploymentOptionsBuildProjectUiBinder extends UiBinder<Widget, DeploymentOptions> {}

	private ProjectDeployer projectDeployer;
	private JSVariableHandler JSVarHandler;
	private HandlerManager eventBus;
	
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField Label baseUrlLabel;
	@UiField TextBox projectNameTextBox;
	@UiField TooltipPanel active;

	public DeploymentOptions(ProjectDeployer projectDeployer, HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		this.projectDeployer = projectDeployer;
		JSVarHandler = new JSVariableHandler();
		baseUrlLabel.setText(JSVarHandler.getDeployerBaseURL());
		setTooltipInitialState();
	}
	
	private boolean validateFields(){
		if(projectNameTextBox.getText().isEmpty()){
			Window.alert("Subdomain required to deploy");
			return false;
		} else if(projectNameTextBox.getText().matches("[a-zA-Z_][a-zA-Z0-9_]*")){
			return true;
		} else {
			Window.alert("Subdomain must start with a letter.");
			return false;
		}
	}
	
	public void setFocus(){
		projectNameTextBox.setFocus(true);
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			eventBus.fireEvent(new PanelTransitionEvent("next", this));
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent("previous", this));
	}
	
	@UiHandler("projectNameTextBox")
	void usernameTextBoxOnFocus(FocusEvent event) {
		active.setVisible(true);
		
		int x = projectNameTextBox.getAbsoluteLeft() + projectNameTextBox.getOffsetWidth() + 5;
		int y = projectNameTextBox.getAbsoluteTop() + 2;
		
		setTooltipPosition(x, y);
		
		active.hide();
		active.setText("This is where the project name stuff goes!");
		active.show();
	}
	
	private void setTooltipInitialState() {
		active.setVisible(false);
	}
	
	private void setTooltipPosition(int x, int y) {
		active.setPopupPosition(x, y);
	}
}
