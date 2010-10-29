package opus.gwt.management.console.client.navigation;


import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.event.AuthenticationEvent;
import opus.gwt.management.console.client.event.AuthenticationEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.UpdateProjectsEvent;
import opus.gwt.management.console.client.event.UpdateProjectsEventHandler;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.resources.NavigationPanelCss.NavigationPanelStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class NavigationPanel extends Composite {

	private static NavigationPanelUiBinder uiBinder = GWT.create(NavigationPanelUiBinder.class);
	interface NavigationPanelUiBinder extends UiBinder<Widget, NavigationPanel> {}

	private final String logoutURL = "/accounts/logout/";
	
	private int projectCount;
	private String deletedProject;
	private EventBus eventBus;
	private PopupPanel projectListPopup;
	
	@UiField HTMLPanel buttonHTMLPanel;
	@UiField Button logoutButton;
	@UiField FormPanel logoutForm;	
	@UiField Button projectsButton;
	@UiField Button loggedInUserButton;
	@UiField Button deployNewButton;
	@UiField NavigationPanelStyle style;
	
	public NavigationPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		projectListPopup = new PopupPanel();
		setupLogoutForm();
	}
	
	public void setEventBus(ClientFactory clientFactory){
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(AuthenticationEvent.TYPE, 
			new AuthenticationEventHandler(){
				public void onAuthentication(AuthenticationEvent event){
					if( event.isAuthenticated() ){
						setUsername(event.getUsername());
					}
		}});
		eventBus.addHandler(UpdateProjectsEvent.TYPE, 
			new UpdateProjectsEventHandler(){
				public void onUpdateProjects(UpdateProjectsEvent event){
					handleProjectNames(event.getProjects());
		}});
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
	
	private void setUsername(String userName){
		this.loggedInUserButton.setText(userName);
	}
	
	@UiHandler("logoutButton")
	void handleLogoutButton(ClickEvent event){
		logoutForm.submit();
	}
	
	@UiHandler("deployNewButton")
	void handleDeployNewButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DEPLOY));
	}
	
	@UiHandler("projectsButton")
	void handleProjectsButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.PROJECTS));
	}
	
	@UiHandler("projectsButton")
	void handleProjectsButtonMouseOver(MouseOverEvent event){
		if(projectCount > 0) {
			int left = projectsButton.getAbsoluteLeft() - ( projectListPopup.getOffsetWidth() / 2 );
			int top = buttonHTMLPanel.getAbsoluteTop() + buttonHTMLPanel.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			projectListPopup.show();
			left = projectsButton.getAbsoluteLeft() + ( projectsButton.getOffsetWidth() / 2 ) - ( projectListPopup.getOffsetWidth() / 2 );
			projectListPopup.setPopupPosition(left, top);
			projectListPopup.show();			
		}
	}

	
	public void handleProjectNames(JsArray<Project> Projects){
		projectListPopup.clear();
		projectCount = Projects.length();
		//iconPanel.projectIconsFlowPanel.clear();
		if(projectCount != 0){
			FlowPanel FP = new FlowPanel();
			for(int i = 0; i < Projects.length(); i++){
				if( !Projects.get(i).getName().equals(deletedProject)){
					final String projectName = Projects.get(i).getName();
					final Label testLabel = new Label(Projects.get(i).getName());
					testLabel.setStyleName(style.popupLabel());
					if( i == Projects.length() - 1 ){
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
				        	eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DASHBOARD, projectName));
				        	projectListPopup.hide();
				        }
				     });
					FP.add(testLabel);
					//iconPanel.addProjectIcon(ProjectNames.get(i).getName());
				}
			}
			projectListPopup.add(FP);
		} else {
			deployNewButton.click();
		}
		projectListPopup.hide();
		projectListPopup.setAutoHideEnabled(true);
		projectListPopup.setStyleName(style.projectsPopup());
	}
}
