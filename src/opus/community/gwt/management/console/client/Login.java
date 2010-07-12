package opus.community.gwt.management.console.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.DockLayoutPanel;
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
	@UiField DockLayoutPanel loginPanel;

	public Login(DeckPanel mainDeckPanel, ManagementConsole managementCon) {
		initWidget(uiBinder.createAndBindUi(this));
		this.managementCon = managementCon;
		loginForm = new FormPanel();
		this.mainDeckPanel = mainDeckPanel;
		JSVarHandler = new JSVariableHandler();
		setupLoginForm();
	}

	private void setupLoginForm(){
		loginForm.setMethod(FormPanel.METHOD_POST);
		loginForm.setVisible(false);
		loginForm.setAction(JSVarHandler.getDeployerBaseURL()+ "accounts/login");
		loginForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        managementCon.loginComplete();
		      }
		 });
	}
	
	@UiHandler("loginButton")
	void onClick(ClickEvent e) {
		FlowPanel formHandler = new FlowPanel();
		loginForm.add(formHandler);
		csrftoken.setValue(Cookies.getCookie("csrftoken")); 
        csrftoken.setName("csrfmiddlewaretoken");
        formHandler.add(csrftoken);
        formHandler.add(usernameTextBox);
        formHandler.add(passwordTextBox);
        mainDeckPanel.add(loginForm);
		loginForm.submit();
	}

}
