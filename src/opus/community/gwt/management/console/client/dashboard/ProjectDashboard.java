package opus.community.gwt.management.console.client.dashboard;

import opus.community.gwt.management.console.client.ServerCommunicator;
import opus.community.gwt.management.console.client.resources.ProjectDashboardCss.ProjectDashboardStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
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
	private int navigationMenuFocusFlag;
	private Label activeLabel;
	
	private DeckPanel mainDeckPanel;
	private FlowPanel navigationMenuPanel;
	private Label titleBarLabel;
	
	@UiField Label dashboardLabel;
	@UiField Label editAppsLabel;
	@UiField Label editProjectLabel;
	@UiField Label deleteProjectLabel;
	@UiField ProjectDashboardStyle style;
	
	public ProjectDashboard(Label titleBarLabel, FlowPanel navigationMenuPanel, DeckPanel mainDeckPanel, String projectTitle, ServerCommunicator ServerComm){
		initWidget(uiBinder.createAndBindUi(this));
		this.titleBarLabel = titleBarLabel;
		this.navigationMenuPanel = navigationMenuPanel;
		this.mainDeckPanel = mainDeckPanel;
		dashboard = new Dashboard();
		deleteProject = new DeleteProject(ServerComm, projectTitle);
		setupTitleBarLabel(projectTitle);
		setupNavigationMenuPanel();
		setupMainDeckPanel();
		mainDeckPanel.showWidget(0);
		navigationMenuFocusFlag = 0;
		activeLabel = dashboardLabel;
		activeLabel.setStyleName(style.navigationLabelActive());
	}
	
	private void setupTitleBarLabel(String projectTitle){
		titleBarLabel.setText(projectTitle);
	}
	
	private void setupNavigationMenuPanel(){
		navigationMenuPanel.add(dashboardLabel);
		navigationMenuPanel.add(editAppsLabel);
		navigationMenuPanel.add(editProjectLabel);
		navigationMenuPanel.add(deleteProjectLabel);
	}
	
	private void setupMainDeckPanel(){
		mainDeckPanel.add(dashboard);
		Dashboard a = new Dashboard();
		Dashboard b = new Dashboard();
		mainDeckPanel.add(a);
		mainDeckPanel.add(b);
		mainDeckPanel.add(deleteProject);
	}
	
	@UiHandler("dashboardLabel")
	void handleDashboardLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != 0){
			  dashboardLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(0);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = dashboardLabel;
			  navigationMenuFocusFlag = 0;
		  }
	 }
	
	@UiHandler("editAppsLabel")
	void handleEditAppsLabel(ClickEvent event){
		  if(navigationMenuFocusFlag != 1){
			  editAppsLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(1);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = editAppsLabel;
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
		  if(navigationMenuFocusFlag != 3){
			  deleteProjectLabel.setStyleName(style.navigationLabelActive());
			  mainDeckPanel.showWidget(3);
			  activeLabel.setStyleName(style.navigationLabel());
			  activeLabel = deleteProjectLabel;
			  navigationMenuFocusFlag = 3;
		  }
	 }
}
