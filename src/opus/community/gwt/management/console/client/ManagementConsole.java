package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.dashboard.ProjectDashboard;
import opus.community.gwt.management.console.client.deployer.applicationDeployer;
import opus.community.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
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
	private int appTypeFlag;
	private PopupPanel pp;
	private Label testLabel;
	
	@UiField Label titleBarLabel;
	@UiField FlowPanel navigationMenuPanel;
	@UiField DeckPanel mainDeckPanel;
	//@UiField Label deployNewProjectLabel;
	//@UiField Label myDashboardsLabel;
	@UiField ManagementConsoleStyle style;
	@UiField Button deployNewButton;
	@UiField Button dashboardsButton;
	@UiField FlowPanel topMenuFlowPanel;
	
	public ManagementConsole() {
		initWidget(uiBinder.createAndBindUi(this));
		appTypeFlag = 1;
		pp = new PopupPanel();
		if(appTypeFlag == 0){
			appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel);
		}
		else {
			projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, "Project Dashboard");
		}
		testLabel = new Label("Test");
		testLabel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	mainDeckPanel.clear();
	    		navigationMenuPanel.clear();
	        	projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel, testLabel.getText()); 
	        	if(pp.isShowing()){
	    			dashboardsButton.setStyleName(style.topDashboardButton());
	    			pp.hide();
	    		}   	
	        }
	     });
		createDashboardsPopup();
	}
	
	private void createDashboardsPopup(){
		FlowPanel FP = new FlowPanel();
		FP.add(testLabel);
		pp.add(FP);
		pp.setStyleName(style.dashboardsPopup());
		testLabel.setStyleName(style.popupLabel());	
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewProjectClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel);
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
			pp.show();
		}
	}
}
