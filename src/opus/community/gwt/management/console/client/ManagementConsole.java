package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.dashboard.ProjectDashboard;
import opus.community.gwt.management.console.client.deployer.applicationDeployer;
import opus.community.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.MenuBar;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class ManagementConsole extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT
			.create(ManagementConsoleUiBinder.class);

	interface ManagementConsoleUiBinder extends
			UiBinder<Widget, ManagementConsole> {
	}

	private applicationDeployer appDeployer;
	private ProjectDashboard projectDashboard;
	private ServerCommunicator ServerComm;
	private int appTypeFlag;
	private PopupPanel pp;
	
	@UiField Label titleBarLabel;
	@UiField FlowPanel navigationMenuPanel;
	@UiField DeckPanel mainDeckPanel;
	@UiField ManagementConsoleStyle style;
	@UiField Button deployNewButton;
	@UiField Button dashboardsButton;
	@UiField FlowPanel topMenuFlowPanel;
	
	public ManagementConsole() {
		initWidget(uiBinder.createAndBindUi(this));
		ServerComm = new ServerCommunicator();
		appTypeFlag = 0;
		pp = new PopupPanel();
		if(appTypeFlag == 0){
			appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel, ServerComm);
		}
		else {
			projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, "Project Dashboard", ServerComm);
		}
		
		createDashboardsPopup();
	}
	
	private void createDashboardsPopup(){
		final String url = URL.encode("https://opus-dev.cnl.ncsu.edu:9007/json/?a&callback=");
		ServerComm.getJson(url, ServerComm, 4, (Object)this);	
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewProjectClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel, ServerComm);
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
	
	public void handleProjectNames(JsArray<ProjectNames> ProjectNames){

		FlowPanel FP = new FlowPanel();
		for(int i = 0; i < ProjectNames.length(); i++){
			final Label testLabel = new Label(ProjectNames.get(i).getName());
			testLabel.setStyleName(style.popupLabel());
			testLabel.addClickHandler(new ClickHandler() {
		        public void onClick(ClickEvent event) {
		        	mainDeckPanel.clear();
		    		navigationMenuPanel.clear();
		        	projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, testLabel.getText(), ServerComm); 
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
	
	public final native JsArray<ProjectNames> asArrayOfProjectNames(JavaScriptObject jso) /*-{
    	return jso;
  	}-*/;
}
