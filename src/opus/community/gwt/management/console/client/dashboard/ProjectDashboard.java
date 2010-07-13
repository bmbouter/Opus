package opus.community.gwt.management.console.client.dashboard;

import opus.community.gwt.management.console.client.ManagementConsole;
import opus.community.gwt.management.console.client.resources.ProjectDashboardCss.ProjectDashboardStyle;

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

public class ProjectDashboard extends Composite {

	private static ProjectDashboardUiBinder uiBinder = GWT
			.create(ProjectDashboardUiBinder.class);

	interface ProjectDashboardUiBinder extends
			UiBinder<Widget, ProjectDashboard> {}

	private Dashboard dashboard;
	private DeleteProject deleteProject;
	private ManageApps manageApps;
	
	private int navigationMenuFocusFlag;
	private Label activeLabel;
	private enum DeckPanels{DASHBOARDPANEL, DELETEPROJECTPANEL};
	
	private DeckPanel mainDeckPanel;
	private FlowPanel navigationMenuPanel;
	private Label titleBarLabel;
	
	@UiField Label dashboardLabel;
	@UiField Label manageAppsLabel;
	@UiField Label editProjectLabel;
	@UiField Label deleteProjectLabel;
	@UiField ProjectDashboardStyle style;
	
	public ProjectDashboard(Label titleBarLabel, FlowPanel navigationMenuPanel, DeckPanel mainDeckPanel, String projectTitle, ManagementConsole managementCon){
		initWidget(uiBinder.createAndBindUi(this));
		this.titleBarLabel = titleBarLabel;
		this.navigationMenuPanel = navigationMenuPanel;
		this.mainDeckPanel = mainDeckPanel;
		dashboard = new Dashboard(projectTitle, managementCon.getServerCommunicator());
		deleteProject = new DeleteProject(projectTitle, managementCon);
		manageApps = new ManageApps();
		setupTitleBarLabel(projectTitle);
		setupNavigationMenuPanel();
		setupMainDeckPanel();
		mainDeckPanel.showWidget(DeckPanels.DASHBOARDPANEL.ordinal());
		navigationMenuFocusFlag = DeckPanels.DASHBOARDPANEL.ordinal();
		activeLabel = dashboardLabel;
		activeLabel.setStyleName(style.navigationLabelActive());
	}
	
	private void setupTitleBarLabel(String projectTitle){
		titleBarLabel.setText(projectTitle);
	}
	
	private void setupNavigationMenuPanel(){
		navigationMenuPanel.add(dashboardLabel);
		//navigationMenuPanel.add(manageAppsLabel);
		//navigationMenuPanel.add(editProjectLabel);
		navigationMenuPanel.add(deleteProjectLabel);
	}
	
	private void setupMainDeckPanel(){
		mainDeckPanel.add(dashboard);
		//mainDeckPanel.add(manageApps);
		//mainDeckPanel.add(new HTML());
		mainDeckPanel.add(deleteProject);
	}
	
	@UiHandler("dashboardLabel")
	void handleDashboardLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != DeckPanels.DASHBOARDPANEL.ordinal()){
			  dashboardLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(DeckPanels.DASHBOARDPANEL.ordinal());
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = dashboardLabel;
			  navigationMenuFocusFlag = DeckPanels.DASHBOARDPANEL.ordinal();
		  }
	 }
	
	@UiHandler("manageAppsLabel")
	void handlemanageAppsLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != 1){
			  manageAppsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(1);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = manageAppsLabel;
			  navigationMenuFocusFlag = 1;
		  }
	 }
	
	@UiHandler("editProjectLabel")
	void handleEditProjectLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != 2){
			  editProjectLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(2);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = editProjectLabel;
			  navigationMenuFocusFlag = 2;
		  }
	 }
	
	@UiHandler("deleteProjectLabel")
	void handleDeleteProjectLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != DeckPanels.DELETEPROJECTPANEL.ordinal()){
			  deleteProjectLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(DeckPanels.DELETEPROJECTPANEL.ordinal());
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = deleteProjectLabel;
			  navigationMenuFocusFlag = DeckPanels.DELETEPROJECTPANEL.ordinal();
		  }
	 }
}
