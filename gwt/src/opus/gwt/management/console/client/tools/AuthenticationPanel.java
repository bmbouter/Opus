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

package opus.gwt.management.console.client.tools;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.AuthenticationEvent;
import opus.gwt.management.console.client.event.GetUserEvent;
import opus.gwt.management.console.client.event.GetUserEventHandler;
import opus.gwt.management.console.client.overlays.User;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class AuthenticationPanel extends Composite {
	
	private static AuthenticationUiBinder uiBinder = GWT.create(AuthenticationUiBinder.class);
	interface AuthenticationUiBinder extends UiBinder<Widget, AuthenticationPanel> {}
	
	private final String loginURL = "/accounts/login/";

	private boolean loggedIn;
	private boolean firstLoginAttempt;
	private EventBus eventBus;
	
	@UiField Hidden csrftoken;
	@UiField Button loginButton;
	@UiField TextBox usernameTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField FormPanel authenticationForm;
	@UiField Label errorLabel;


	public AuthenticationPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = clientFactory.getEventBus();
		loggedIn = false;
		firstLoginAttempt = true;
		registerHandlers();
		setupAuthenticationForm();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(GetUserEvent.TYPE, 
			new GetUserEventHandler(){
				public void onGetUser(GetUserEvent event){
					handleUserInformation(event.getUser());
				}
		});
	}
	
	private void setupAuthenticationForm(){
		authenticationForm.setMethod(FormPanel.METHOD_POST);
		authenticationForm.setAction(loginURL);
		authenticationForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		    	  if( event.getResults().contains("Please try again.") ){
		    		  if( firstLoginAttempt )
			    	  		firstLoginAttempt = false;
		    		  loginFailed();
		    	  } else {
		    		  loginSucceed();
		    	  }
		      }
		 });
		csrftoken.setValue(Cookies.getCookie("csrftoken")); 
        csrftoken.setName("csrfmiddlewaretoken");
	}
	
	private void loginFailed(){
		loggedIn = false;
		usernameTextBox.setFocus(true);
		if( !firstLoginAttempt ){
			errorLabel.setVisible(true);
			usernameTextBox.setText("");
			passwordTextBox.setText("");
		} 
	}
	
	private void loginSucceed(){
		loggedIn = true;
		eventBus.fireEvent(new AuthenticationEvent());	
	}
	
	public void handleUserInformation(User userInfo){
		if( userInfo.isAuthenticated() ){
		
		} else {
			
		}
	}
		
	@UiHandler("loginButton")
	void onLoginClick(ClickEvent event) {
		authenticationForm.submit();
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
	
	public boolean isLoggedIn(){
		return loggedIn;
	}
}