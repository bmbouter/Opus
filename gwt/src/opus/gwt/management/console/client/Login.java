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

package opus.gwt.management.console.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class Login extends Composite {

	private static LoginUiBinder uiBinder = GWT.create(LoginUiBinder.class);

	interface LoginUiBinder extends UiBinder<Widget, Login> {
	}

	private FormPanel loginForm; 
	private DeckPanel mainDeckPanel;
	private JSVariableHandler JSVarHandler;
	private ManagementConsole managementCon;
	
	@UiField Hidden csrftoken;
	@UiField Button loginButton;
	@UiField TextBox usernameTextBox;
	@UiField PasswordTextBox passwordTextBox;


	public Login(DeckPanel mainDeckPanel, ManagementConsole managementCon) {
		initWidget(uiBinder.createAndBindUi(this));
		this.managementCon = managementCon;
		this.mainDeckPanel = mainDeckPanel;
		JSVarHandler = new JSVariableHandler();
		loginForm = new FormPanel();
		setupLoginForm();
	}

	private void setupLoginForm(){
		loginForm.setMethod(FormPanel.METHOD_POST);
		loginForm.setVisible(false);
		loginForm.setAction(JSVarHandler.getDeployerBaseURL() + "/accounts/login");
		loginForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        managementCon.checkLogin();
		      }
		 });
	}
	
	@UiHandler("loginButton")
	void onLoginClick(ClickEvent event) {
		handleLoginButton();
	}

	@UiHandler("loginButton")
	void onKeyPressLogin(KeyPressEvent event){
		if(event.getCharCode() == KeyCodes.KEY_ENTER){
			loginButton.click();
		}
	}
	
	@UiHandler("usernameTextBox")
	void onKeyPressUsername(KeyPressEvent event){
		if(event.getCharCode() == KeyCodes.KEY_ENTER){
			loginButton.click();
		}
	}
	
	@UiHandler("passwordTextBox")
	void onKeyPressPassword(KeyPressEvent event){
		if(event.getCharCode() == KeyCodes.KEY_ENTER){
			loginButton.click();
		}
	}

	private void handleLoginButton(){
		FlowPanel formHandler = new FlowPanel();
		csrftoken.setValue(Cookies.getCookie("csrftoken")); 
        csrftoken.setName("csrfmiddlewaretoken");
        formHandler.add(csrftoken);
        formHandler.add(usernameTextBox);
        formHandler.add(passwordTextBox);
        loginForm.add(formHandler);
        mainDeckPanel.add(loginForm);
		loginForm.submit();
	}
	
}