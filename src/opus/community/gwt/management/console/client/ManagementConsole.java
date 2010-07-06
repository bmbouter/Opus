package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.dashboard.ProjectDashboard;
import opus.community.gwt.management.console.client.deployer.applicationDeployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Label;
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
	
	@UiField Label titleBarLabel;
	@UiField FlowPanel navigationMenuPanel;
	@UiField DeckPanel mainDeckPanel;
	@UiField Label deployNewProjectLabel;
	
	public ManagementConsole() {
		initWidget(uiBinder.createAndBindUi(this));
		appTypeFlag = 1;
		appDeployer = new applicationDeployer(titleBarLabel, navigationMenuPanel, mainDeckPanel);
		appDeployer.setVisible(false);
		projectDashboard = new ProjectDashboard(titleBarLabel, navigationMenuPanel, mainDeckPanel);
		appDeployer.setVisible(true);
		if(appTypeFlag == 0){
		}
		else {
			
		}
	}
	
	@UiHandler("deployNewProjectLabel")
	void handleDeployNewProjectClick(ClickEvent event){
		appDeployer.setVisible(true);
		projectDashboard.setVisible(false); 
	}
}
