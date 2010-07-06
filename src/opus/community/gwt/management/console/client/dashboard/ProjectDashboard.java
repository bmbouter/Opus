package opus.community.gwt.management.console.client.dashboard;

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

	private DeckPanel mainDeckPanel;
	private FlowPanel navigationMenuPanel;
	private Label titleBarLabel;
	
	@UiField Label dashboardLabel;
	@UiField Label addAppsLabel;
	@UiField Label editAppsLabel;
	
	public ProjectDashboard(Label titleBarLabel, FlowPanel navigationMenuPanel, DeckPanel mainDeckPanel){
		initWidget(uiBinder.createAndBindUi(this));
		this.titleBarLabel = titleBarLabel;
		this.navigationMenuPanel = navigationMenuPanel;
		this.mainDeckPanel = mainDeckPanel;
		setupTitleBarLabel();
		setupNavigationMenuPanel();
		setupMainDeckPanel();
	}
	
	private void setupTitleBarLabel(){
		titleBarLabel.setText("Project Dashboard");
	}
	
	private void setupNavigationMenuPanel(){
		navigationMenuPanel.add(dashboardLabel);
		navigationMenuPanel.add(addAppsLabel);
		navigationMenuPanel.add(editAppsLabel);
	}
	
	private void setupMainDeckPanel(){
		
	}
}
