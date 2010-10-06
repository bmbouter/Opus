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

import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;
import opus.gwt.management.console.client.resources.ProjectOptionsCss.ProjectOptionsStyle;
import opus.gwt.management.console.client.resources.TooltipPanelCss.TooltipPanelStyle;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Style;
import com.google.gwt.event.dom.client.BlurEvent;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class ProjectOptions extends Composite {

	private static BuildProjectPage2UiBinder uiBinder = GWT.create(BuildProjectPage2UiBinder.class);
	interface BuildProjectPage2UiBinder extends UiBinder<Widget, ProjectOptions> {}
	
	private ProjectDeployer projectDeployer;
	private HandlerManager eventBus;
	
	@UiField TextBox usernameTextBox;
	@UiField TextBox emailTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField PasswordTextBox passwordConfirmTextBox;
	@UiField Button nextButton;
	@UiField Button previousButton;
	@UiField HTMLPanel projectOptionsPanel;
	@UiField ListBox idProvider;
	@UiField TooltipPanel active;
	@UiField ProjectOptionsStyle style;
	@UiField Label passwordError;
	@UiField Label emailError;
	
	public ProjectOptions(ProjectDeployer projectDeployer, HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.projectDeployer = projectDeployer;
		this.eventBus = eventBus;
		setTooltipInitialState();
		passwordError.setText("");
		emailError.setText("");
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
	
	@UiHandler("usernameTextBox")
	void usernameTextBoxOnFocus(FocusEvent event) {
		active.setVisible(true);
		
		int x = getTooltipPosition(usernameTextBox)[0];
		int y = getTooltipPosition(usernameTextBox)[1];
			
		active.setGray();
		setTooltipPosition(x, y);
		setTooltipText("Optional Field. Enter username if you wish to create a superuser.");
	}
	
	@UiHandler("passwordTextBox")
	void passwordTextBoxOnFocus(FocusEvent event) {
		if(isPasswordValid()) {
			active.setVisible(true);
			
			int x = getTooltipPosition(passwordTextBox)[0];
			int y = getTooltipPosition(passwordTextBox)[1];
			
			active.setGray();
			setTooltipPosition(x, y);
			setTooltipText("Must be entered if your wish to create a superuser.");
		}
	}
	
	@UiHandler("passwordConfirmTextBox")
	void passwordConfirmTextBoxOnFocus(FocusEvent event) {
		if(isPasswordValid()) {
			active.setVisible(true);
	
			int x = getTooltipPosition(passwordConfirmTextBox)[0];
			int y = getTooltipPosition(passwordConfirmTextBox)[1];
			
			active.setGray();
			setTooltipPosition(x, y);
			setTooltipText("Confirm the previous password.");
		}
	}
	
	@UiHandler("emailTextBox")
	void emailTextBoxOnFocus(FocusEvent event) {
		if(isEmailValid()) {
			active.setVisible(true);
			
			int x = getTooltipPosition(emailTextBox)[0];
			int y = getTooltipPosition(emailTextBox)[1];
			
			active.setGray();
			setTooltipPosition(x, y);
			setTooltipText("Enter your email address.");
		}
	}
	
	@UiHandler("usernameTextBox")
	void usernameTextBoxOnChange(KeyUpEvent event) {
		if(!usernameTextBox.getText().isEmpty() && !isEmailValid()
				&& !isPasswordValid()) {
			setAllStyles();
			passwordError.setText("Passwords do not match");
			emailError.setText("Enter a valid email address");
		} else {
			removeAllStyles();
			passwordError.setText("");
			emailError.setText("");
		}
	}
	
	@UiHandler("passwordTextBox")
	void passwordTextBoxOnChange(KeyUpEvent event) {
		if(!usernameTextBox.getText().isEmpty()) {
			if(!isPasswordValid()) {
				active.hide();
				passwordError.setText("Passwords do not match");
				passwordTextBox.setStyleName(style.redBorder());
				passwordConfirmTextBox.setStyleName(style.redBorder());
			} else {
				passwordError.setText("");
				passwordTextBox.removeStyleName(style.redBorder());
				passwordConfirmTextBox.removeStyleName(style.redBorder());
			}
		} else {
			
		}
	}
	
	@UiHandler("passwordConfirmTextBox")
	void passwordConfirmTextBoxOnChange(KeyUpEvent event) {
		if(!usernameTextBox.getText().isEmpty()) {
			if(!isPasswordValid()) {
				active.hide();
				passwordError.setText("Passwords do not match");
				passwordTextBox.setStyleName(style.redBorder());
				passwordConfirmTextBox.setStyleName(style.redBorder());
			} else {
				passwordError.setText("");
				passwordTextBox.removeStyleName(style.redBorder());
				passwordConfirmTextBox.removeStyleName(style.redBorder());
			}
		} else {
			
		}
	}
	
	@UiHandler("emailTextBox")
	void emailTextBoxOnChange(KeyUpEvent event) {
		if(!usernameTextBox.getText().isEmpty()) {
			if(!isEmailValid()) {
				active.hide();
				
				emailTextBox.setStyleName(style.redBorder());
			} else {
				emailError.setText("");
				emailTextBox.removeStyleName(style.redBorder());
			}
		} else {
			
		}
	}
	
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		if(validateFields()){
			eventBus.fireEvent(new PanelTransitionEvent("next", this));
		} else {
			Window.alert("Validation error");
		}
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent("previous", this));
	}
	
	public void setFocus(){
		usernameTextBox.setFocus(true);
	}
	
	public boolean validateFields(){
		if(!usernameTextBox.getText().isEmpty()) {
			if(passwordTextBox.getText().isEmpty()) {
				return false;
			} else if(!passwordTextBox.getText().equals(passwordConfirmTextBox.getText())) {
				return false;
			} else if (isEmailValid()) {
				return false;
			}
		}
		
		return true;
	}
	
	private void setAllStyles() {
		passwordTextBox.setStyleName(style.redBorder());
		passwordConfirmTextBox.setStyleName(style.redBorder());
		emailTextBox.setStyleName(style.redBorder());
	}
	
	private void removeAllStyles() {
		passwordTextBox.removeStyleName(style.redBorder());
		passwordConfirmTextBox.removeStyleName(style.redBorder());
		emailTextBox.removeStyleName(style.redBorder());
	}
	
	private boolean isEmailValid() {
		if(emailTextBox.getText().isEmpty()) {
			return false;
		} else if(!emailTextBox.getText().matches("[^@]+@[^@]+\\.\\w+")) {
			return false;
		}
		
		return true;
	}
	
	private boolean isPasswordValid() {
		if(passwordTextBox.getText().isEmpty()) {
			return false;
		} else if(!passwordTextBox.getText().equals(passwordConfirmTextBox.getText())) {
			return false;
		}
		
		return true;
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
