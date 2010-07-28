package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.dashboard.ProjectDashboard;
import opus.community.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class IconPanel extends Composite {

	@UiField ManagementConsoleStyle style;
	
	private static IconPanelUiBinder uiBinder = GWT
			.create(IconPanelUiBinder.class);

	interface IconPanelUiBinder extends UiBinder<Widget, IconPanel> {
	}
	
	
	private ManagementConsole console;
	private ProjectDashboard projectDashboard;
	
	@UiField ScrollPanel iconScrollPanel;
	@UiField FlowPanel projectIconsFlowPanel;

	public IconPanel(ManagementConsole console) {
		initWidget(uiBinder.createAndBindUi(this));
		this.console = console;
	}
	
	public void addProjectIcon(String name) {
		HTML project = new HTML();
		project.setHTML("<img src='http://openiconlibrary.sourceforge.net/gallery2/Icons/devices/blockdevice-2.png' width='128' height='128'/><br/>"+name);
		
		final String projectName = name;
		
		
		final FocusPanel testLabel = new FocusPanel();
		testLabel.add(project);
		testLabel.setStyleName(style.projectIcon());
		testLabel.addMouseOverHandler(new MouseOverHandler(){
			public void onMouseOver(MouseOverEvent event){
				testLabel.setStyleName(style.projectIconActive());
			}
		});
		testLabel.addMouseOutHandler(new MouseOutHandler(){
			public void onMouseOut(MouseOutEvent event){
				testLabel.setStyleName(style.projectIcon());
			}
		});
		testLabel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	console.mainDeckPanel.clear();
	        	console.navigationMenuPanel.clear();
	        	projectDashboard = new ProjectDashboard(console.titleBarLabel, console.navigationMenuPanel, console.mainDeckPanel, projectName, console); 

	        	/*if(pp.isShowing()){
	    			dashboardsButton.setStyleName(style.topDashboardButton());
	    			pp.hide();
	    		} */ 
	        	testLabel.setStyleName(style.projectIcon());
	        }
	     });
		projectIconsFlowPanel.add(testLabel);
		
	}
	

}
