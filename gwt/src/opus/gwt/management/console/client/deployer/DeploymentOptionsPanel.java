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
import opus.gwt.management.console.client.event.DeployProjectEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class DeploymentOptionsPanel extends Composite {

	private static DeploymentOptionsBuildProjectUiBinder uiBinder = GWT.create(DeploymentOptionsBuildProjectUiBinder.class);
	interface DeploymentOptionsBuildProjectUiBinder extends UiBinder<Widget, DeploymentOptionsPanel> {}

	private JSVariableHandler JSVarHandler;
	private HandlerManager eventBus;
	private String projectName;
	
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField Label baseProtocolLabel;
	@UiField Label baseDomainLabel;
	@UiField Label subDomainLabel;
	@UiField TextBox projectNameTextBox;
	@UiField TooltipPanel active;
	@UiField ProjectDeployerStyle deployer;
	@UiField CheckBox debugCheckBox;
	@UiField Label error;

	public DeploymentOptionsPanel(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		projectName = "";
		JSVarHandler = new JSVariableHandler();
		baseProtocolLabel.setText(JSVarHandler.getDeployerBaseURL().split("//")[0] + "//");
		baseDomainLabel.setText(JSVarHandler.getDeployerBaseURL().split("//")[1]);
		setTooltipInitialState();
		error.setText("");
	}
	
	private boolean validateFields(){
		if(projectNameTextBox.getText().isEmpty()){
			projectNameTextBox.setStyleName(deployer.redBorder());
			error.setText("Subdomain required to deploy");
			return false;
		} else if(projectNameTextBox.getText().matches("[a-zA-Z_][a-zA-Z0-9_]*")){
			return true;
		} else {
			projectNameTextBox.setStyleName(deployer.redBorder());
			error.setText("Can only contain letters.");
			return false;
		}
	}
	
	public void setFocus(){
		projectNameTextBox.setFocus(true);
	}
	
	public String getProjectName(){
		return projectName;
	}
	
	public String getPostData(){
		StringBuffer postData = new StringBuffer();
		postData.append("&debug=");
		postData.append(debugCheckBox.getValue());
		return postData.toString();
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if( validateFields() ){
			projectName = projectNameTextBox.getText();
			eventBus.fireEvent(new DeployProjectEvent());
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.PREVIOUS, this));
	}
	
	@UiHandler("projectNameTextBox")
	void projectNameTextBoxOnFocus(FocusEvent event) {
		if(projectNameTextBox.getStyleName().equals(deployer.greyBorder())) {
			active.setVisible(true);
			
			int x = getTooltipPosition(projectNameTextBox)[0];
			int y = getTooltipPosition(projectNameTextBox)[1];
			
			setTooltipPosition(x, y);
			setTooltipText("Enter a subdomain name for your project");
		}
	}
	
	@UiHandler("projectNameTextBox")
	void projectNameTextboxOnKeyUp(KeyUpEvent event){
		subDomainLabel.setText(projectNameTextBox.getText() + ".");
		if(projectNameTextBox.getText().isEmpty()) {
			error.setText("Subdomain required to deploy");
			projectNameTextBox.setStyleName(deployer.redBorder());
			active.hide();
			subDomainLabel.setText("");
		} else {
			active.show();
			projectNameTextBox.setStyleName(deployer.greyBorder());
			error.setText("");
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
}
