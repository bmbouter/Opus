package opus.gwt.management.console.client.navigation;


import java.util.HashMap;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.event.AddProjectEvent;
import opus.gwt.management.console.client.event.AddProjectEventHandler;
import opus.gwt.management.console.client.event.DeleteProjectEvent;
import opus.gwt.management.console.client.event.DeleteProjectEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.resources.NavigationPanelCss.NavigationPanelStyle;

import com.google.gwt.core.client.GWT;
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
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class NavigationPanel extends Composite {

	private static NavigationPanelUiBinder uiBinder = GWT.create(NavigationPanelUiBinder.class);
	interface NavigationPanelUiBinder extends UiBinder<Widget, NavigationPanel> {}

	private final String logoutURL = "/accounts/logout/";
	
	private int projectCount;
	private EventBus eventBus;
	private PopupPanel projectListPopup;
	private FlowPanel projectNamesFlowPanel;
	private ClientFactory clientFactory;
	private HashMap<String, Label> projectLabels;
	
	@UiField HTMLPanel buttonHTMLPanel;
	@UiField Button logoutButton;
	@UiField FormPanel logoutForm;	
	@UiField Button projectsButton;
	@UiField Button loggedInUserButton;
	@UiField Button deployNewButton;
	@UiField NavigationPanelStyle style;
	
	public NavigationPanel(ClientFactory clientFactory) {
		this.clientFactory = clientFactory;
		this.eventBus = clientFactory.getEventBus();
		projectListPopup = new PopupPanel();
		projectNamesFlowPanel = new FlowPanel();
		projectLabels = new HashMap<String, Label>();
		registerHandlers();
		setUsername(clientFactory.getJSVariableHandler().getUser());
		handleProjectNames(clientFactory.getProjects());
		setupLogoutForm();
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	private void registerHandlers(){
		eventBus.addHandler(AddProjectEvent.TYPE, 
			new AddProjectEventHandler(){
				public void onAddProject(AddProjectEvent event){
					addProject(event.getProject());
		}});
		eventBus.addHandler(DeleteProjectEvent.TYPE, 
				new DeleteProjectEventHandler(){
					public void onDeleteProject(DeleteProjectEvent event) {
						removeProject(event.getProjectName());
					}
		});
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
		if(projectNamesFlowPanel.getWidgetCount() > 0) {
			int left = projectsButton.getAbsoluteLeft() - ( projectListPopup.getOffsetWidth() / 2 );
			int top = buttonHTMLPanel.getAbsoluteTop() + buttonHTMLPanel.getOffsetHeight();
			projectListPopup.setPopupPosition(left, top);
			projectListPopup.show();
			left = projectsButton.getAbsoluteLeft() + ( projectsButton.getOffsetWidth() / 2 ) - ( projectListPopup.getOffsetWidth() / 2 );
			projectListPopup.setPopupPosition(left, top);
			projectListPopup.show();			
		}
	}

	public void handleProjectNames(HashMap<String, Project> Projects){
		projectListPopup.clear();
		projectNamesFlowPanel.clear();
	
		for(String key : Projects.keySet()){
			addProject(Projects.get(key));
		}
		projectListPopup.add(projectNamesFlowPanel);
		projectListPopup.hide();
		projectListPopup.setAutoHideEnabled(true);
		projectListPopup.setStyleName(style.projectsPopup());
	}
	
	private void addProject(Project project){
		final String projectName = project.getName();
		final Label testLabel = new Label(project.getName());
		testLabel.setStyleName(style.popupLabel());
		testLabel.addStyleName(style.lastLabel());	
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
		testLabel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DASHBOARD, projectName));
	        	projectListPopup.hide();
	        }
	     });
		
		projectNamesFlowPanel.add(testLabel);
		projectLabels.put(projectName, testLabel);
	}
	
	private void removeProject(String projectName){
		projectNamesFlowPanel.remove(projectLabels.remove(projectName));
	}
}
