package opus.gwt.management.console.client.navigation;

import java.util.HashMap;

import opus.gwt.management.console.client.event.PanelTransitionEvent;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class NavigationPanel extends Composite {

	private static NavigationPanelUiBinder uiBinder = GWT.create(NavigationPanelUiBinder.class);
	interface NavigationPanelUiBinder extends UiBinder<Widget, NavigationPanel> {}

	private final String logoutURL = "/accounts/logout/";
	
	private PopupPanel projectListPopup;
	private int projectCount;
	private String deletedProject;
	private HashMap<String, Integer> mainPanels;
	private HandlerManager eventBus;
	
	@UiField Button logoutButton;
	@UiField FormPanel logoutForm;	
	@UiField Button projectsButton;
	@UiField Button loggedInUserButton;
	
	public NavigationPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		setupLogoutForm();
	}
	
	public void setEventBus(HandlerManager eventBus){
		this.eventBus = eventBus;
	}
	
	private void setupLogoutForm(){
		logoutForm.setMethod(FormPanel.METHOD_GET);
		logoutForm.setAction(logoutURL);
		logoutForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		    	  Window.Location.reload();
		      }
		 });
	}
	
	@UiHandler("logoutButton")
	void handleLogoutButton(ClickEvent event){
		logoutForm.submit();
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent("deploy"));
	}
	
	@UiHandler("projectsButton")
	void handleProjectsButton(ClickEvent event){
		
	}
	
	/*
	private void createDashboardsPopup(){
		final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + projectsURL);
		//serverComm.getJson(url, "handleProjectNames");	
	}
	
	private void setupProjectPopup(){
		projectListPopup.setAutoHideEnabled(true);
		projectListPopup.addCloseHandler(new CloseHandler<PopupPanel>(){
			public void onClose(CloseEvent<PopupPanel> event){
				dashboardsButton.setStyleName(style.topDashboardButton());
			}
		});
	}
	
	@UiHandler("dashboardsButton")
	void handleDashboardsButtonMouseOver(MouseOverEvent event){
		if(projectCount > 0) {
			dashboardsButton.setStyleName(style.topDashboardButtonActive());
			int left = dashboardsButton.getAbsoluteLeft();
			int top = dashboardsButton.getAbsoluteTop() + dashboardsButton.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			int width = dashboardsButton.getOffsetWidth();
			projectListPopup.setWidth(Integer.toString(width) + "px");
			projectListPopup.show();
		}
	}
	
	@UiHandler("dashboardsButton")
	void handleDashboardsButtonClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
		mainDeckPanel.add(iconPanel);
		mainDeckPanel.showWidget(0);
		if(projectListPopup.isShowing()){
			projectListPopup.hide();
		} else {
			dashboardsButton.setStyleName(style.topDashboardButtonActive());
			int left = dashboardsButton.getAbsoluteLeft();
			int top = dashboardsButton.getAbsoluteTop() + dashboardsButton.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			int width = dashboardsButton.getOffsetWidth();
			projectListPopup.setWidth(Integer.toString(width) + "px");
			projectListPopup.show();
		}
		projectListPopup.hide();
	}
	
	public void handleProjectNames(JsArray<ProjectNames> ProjectNames){
		projectListPopup.clear();
		projectCount = ProjectNames.length();
		iconPanel.projectIconsFlowPanel.clear();
		if(projectCount != 0){
			FlowPanel FP = new FlowPanel();
			for(int i = 0; i < ProjectNames.length(); i++){
				if( !ProjectNames.get(i).getName().equals(deletedProject)){
					final Label testLabel = new Label(ProjectNames.get(i).getName());
					testLabel.setStyleName(style.popupLabel());
					if( i == ProjectNames.length() - 1 ){
						testLabel.addStyleName(style.lastLabel());	
						testLabel.addMouseOverHandler(new MouseOverHandler(){
							public void onMouseOver(MouseOverEvent event){
								testLabel.setStyleName(style.popupLabelActive());
								testLabel.addStyleName(style.lastLabel());
							}
						});
						testLabel.addMouseOutHandler(new MouseOutHandler(){
							public void onMouseOut(MouseOutEvent event){
								testLabel.setStyleName(style.popupLabel());
								testLabel.addStyleName(style.lastLabel());
							}
						});
					} else {
					testLabel.addMouseOverHandler(new MouseOverHandler(){
						public void onMouseOver(MouseOverEvent event){
								testLabel.setStyleName(style.popupLabelActive());
							}
						});
						testLabel.addMouseOutHandler(new MouseOutHandler(){
							public void onMouseOut(MouseOutEvent event){
								testLabel.setStyleName(style.popupLabel());
							}
						});
					}
					testLabel.addClickHandler(new ClickHandler() {
				        public void onClick(ClickEvent event) {
				        	mainDeckPanel.clear();
				    		navigationMenuPanel.clear();
				        	projectManager = new ProjectManager(eventBus); 
				        	if(projectListPopup.isShowing()){
				    			dashboardsButton.setStyleName(style.topDashboardButton());
				    			projectListPopup.hide();
				    		}   	
				        }
				     });
					FP.add(testLabel);
					iconPanel.addProjectIcon(ProjectNames.get(i).getName());
				}
			}
			projectListPopup.add(FP);
			mainDeckPanel.add(iconPanel);
			mainDeckPanel.showWidget(0);
		} else {
			
			deployNewButton.click();
		}
		projectListPopup.setStyleName(style.dashboardsPopup());
	}

	public void onDeployNewProject(String projectName){
		createDashboardsPopup();
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
    	projectManager = new ProjectManager(eventBus);
	}
	
	public void onProjectDelete(String deletedProject){
		this.deletedProject = deletedProject;
		createDashboardsPopup();
		iconPanel.removeProjectIcon(deletedProject);
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		titleBarLabel.setText("");
	}
	
	public JSVariableHandler getJSVariableHandler(){
		return JSVarHandler;
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewProjectClick(ClickEvent event){
		mainDeckPanel.clear();
		navigationMenuPanel.clear();
		projectDeployer = new ProjectDeployer(eventBus);
	}
	*/
}
