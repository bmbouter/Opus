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
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AuthenticationPanel extends Composite {
	
	private static AuthenticationUiBinder uiBinder = GWT.create(AuthenticationUiBinder.class);
	interface AuthenticationUiBinder extends UiBinder<Widget, AuthenticationPanel> {}
	
	private final String loginURL = "/accounts/login/";

	private boolean loggedIn;
	private boolean firstLoginAttempt;
	private ClientFactory clientFactory;
	
	@UiField Hidden csrftoken;
	@UiField Button loginButton;
	@UiField TextBox usernameTextBox;
	@UiField PasswordTextBox passwordTextBox;
	@UiField FormPanel authenticationForm;
	@UiField Label errorLabel;


	public AuthenticationPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.clientFactory = clientFactory;
		loggedIn = false;
		firstLoginAttempt = true;
		if( !clientFactory.getJSVariableHandler().getUser().equals("") ){
			loginSucceeded();
		} else {
			RootPanel.get().add(this);
		}
	}
	
	private void onLogin(boolean success){
		if( !success ){
  		  if( firstLoginAttempt )
	    	  		firstLoginAttempt = false;
  		  loginFailed();
  	  } else {
  		  loginSucceeded();
  	  }
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
	
	private void loginSucceeded(){
		loggedIn = true;
		ManagementConsoleController mcc = new ManagementConsoleController(clientFactory);
	}
	
	private void submitLogin(){
		StringBuffer formBuilder = new StringBuffer();
		formBuilder.append("csrfmiddlewaretoken=");
		formBuilder.append( URL.encodeQueryString(clientFactory.getJSVariableHandler().getCSRFTokenURL()));
		
		formBuilder.append("&username=");
		formBuilder.append( URL.encodeQueryString(usernameTextBox.getText()));
		formBuilder.append("&password=");
		formBuilder.append( URL.encodeQueryString(passwordTextBox.getText()));
				
	    RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, loginURL);
	    builder.setHeader("Content-type", "application/x-www-form-urlencoded");
	    
	    try {
	      Request request = builder.sendRequest(formBuilder.toString(), new RequestCallback() {
	        public void onError(Request request, Throwable exception) {
	        	Window.alert(exception.getMessage());
	        }

	        public void onResponseReceived(Request request, Response response) {
	        	if( response.getText().contains("Please try again.") ){	
	        		onLogin(false);
	        	} else {
	        		onLogin(true);
	        	}
	        }});
	    } catch (RequestException e) {
	    	
	    }

	}
		
	@UiHandler("loginButton")
	void onLoginClick(ClickEvent event) {
		submitLogin();
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