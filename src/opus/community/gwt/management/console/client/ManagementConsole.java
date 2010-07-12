package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.dashboard.ProjectDashboard;
import opus.community.gwt.management.console.client.deployer.applicationDeployer;
import opus.community.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class ManagementConsole extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT
			.create(ManagementConsoleUiBinder.class);

	interface ManagementConsoleUiBinder extends
			UiBinder<Widget, ManagementConsole> {
	}

	private applicationDeployer appDeployer;
	private ProjectDashboard projectDashboard;
	private ServerCommunicator ServerComm;
	private ManagementConsole managementCon;
	private JSVariableHandler JSVarHandler;
	private int appTypeFlag;
	private PopupPanel pp;
	
	@UiField Label titleBarLabel;
	@UiField FlowPanel navigationMenuPanel;
	@UiField DeckPanel mainDeckPanel;
	@UiField ManagementConsoleStyle style;
	@UiField Button deployNewButton;
	@UiField Button dashboardsButton;
	@UiField FlowPanel topMenuFlowPanel;
	@UiField Button loggedInUserButton;
	@UiField Button authenticationButton;
	
	public ManagementConsole() {
		initWidget(uiBinder.createAndBindUi(this));
		JSVarHandler = new JSVariableHandler();
		managementCon = this;
		ServerComm = new ServerCommunicator();
		checkLogin();
		pp = new PopupPanel();
		createDashboardsPopup();
	}
	
	public void checkLogin(){
		final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + "/json/username/?a&callback=");
		ServerComm.getJson(url, ServerComm, 6, (Object)this);
	}
	
	private void createDashboardsPopup(){
		final String url = URL.encode("https://opus-dev.cnl.ncsu.edu:9007/json/?a&callback=");
		ServerComm.getJson(url, ServerComm, 4, (Object)this);	
	}
	
	public void onDeployNewProject(String projectName){
		createDashboardsPopup();
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
    	projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, projectName, managementCon);
	}
	
	public void onProjectDelete(){
		createDashboardsPopup();
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
	}
	
	public ServerCommunicator getServerCommunicator(){
		return ServerComm;
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewProjectClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel, managementCon);
	}
	
	@UiHandler("dashboardsButton")
	void handleDashboardsButton(ClickEvent event){
		if(pp.isShowing()){
			dashboardsButton.setStyleName(style.topDashboardButton());
			pp.hide();
		} else {
			dashboardsButton.setStyleName(style.topDashboardButtonActive());
			int left = dashboardsButton.getAbsoluteLeft();
			int top = dashboardsButton.getAbsoluteTop() + dashboardsButton.getOffsetHeight();
			pp.setPopupPosition(left, top);
			int width = dashboardsButton.getOffsetWidth();
			pp.setWidth(Integer.toString(width) + "px");
			pp.show();
		}
	}
	
	@UiHandler("authenticationButton")
	void handleAuthenticationButton(ClickEvent event){
		if(authenticationButton.getText().equals("Logout")){
			FormPanel logoutForm = new FormPanel();
			logoutForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
			      public void onSubmitComplete(SubmitCompleteEvent event) {
			        checkLogin();
			      }
			 });
			logoutForm.setMethod(FormPanel.METHOD_GET);
			logoutForm.setAction(JSVarHandler.getDeployerBaseURL() + "/accounts/logout/");
			mainDeckPanel.add(logoutForm);
			logoutForm.submit();
		} else {
			showLoginPanel();
		}
	}
	
	public void handleProjectNames(JsArray<ProjectNames> ProjectNames){
		pp.clear();
		FlowPanel FP = new FlowPanel();
		for(int i = 0; i < ProjectNames.length(); i++){
			final Label testLabel = new Label(ProjectNames.get(i).getName());
			testLabel.setStyleName(style.popupLabel());
			testLabel.addClickHandler(new ClickHandler() {
		        public void onClick(ClickEvent event) {
		        	mainDeckPanel.clear();
		    		navigationMenuPanel.clear();
		        	projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, testLabel.getText(), managementCon); 
		        	if(pp.isShowing()){
		    			dashboardsButton.setStyleName(style.topDashboardButton());
		    			pp.hide();
		    		}   	
		        }
		     });
			FP.add(testLabel);		
		}
		pp.add(FP);
		pp.setStyleName(style.dashboardsPopup());
	}
	
	public void handleUserInformation(UserInformation userInfo){
		if(userInfo.isAuthenticated()){
			loggedInUserButton.setText("Logged in as: " + userInfo.getUsername());
			loggedInUserButton.setVisible(true);
		} else {
			showLoginPanel();
		}
	}
	
	private void showLoginPanel(){
		authenticationButton.setText("Login");
		FlowPanel formHolder = new FlowPanel();
		TextBox usernameTextBox = new TextBox();
		PasswordTextBox passwordTextBox = new PasswordTextBox();
		formHolder.add(usernameTextBox);
		formHolder.add(passwordTextBox);
		FormPanel loginForm = new FormPanel();
		loginForm.add(formHolder);
		formHolder.add(new Button("Login"));
		mainDeckPanel.add(formHolder);
		mainDeckPanel.showWidget(0);
		loggedInUserButton.setVisible(false);
	}
	
	public final native JsArray<ProjectNames> asArrayOfProjectNames(JavaScriptObject jso) /*-{
    	return jso;
  	}-*/;
	
	public final native UserInformation asJSOUserInformation(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}
