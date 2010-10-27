/*############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
############################################################################*/

package opus.gwt.management.console.client.dashboard;

import java.util.HashMap;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.resources.ManagementConsoleControllerResources.ManagementConsoleControllerStyle;
import opus.gwt.management.console.client.tools.DescriptionPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JsArrayString;
import com.google.gwt.event.dom.client.ClickEvent;
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
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupListener;
import com.google.gwt.user.client.ui.Widget;

public class DashboardPanel extends Composite {

	private static DashboardUiBinder uiBinder = GWT.create(DashboardUiBinder.class);
	interface DashboardUiBinder extends UiBinder<Widget, DashboardPanel> {}
	
	private boolean active;
	private EventBus eventBus;
	private ClientFactory clientFactory;
	private DescriptionPanel desc;
	private HashMap<String, Application> applications;
	private JSVariableHandler JSVarHandler;
	private String projectName;
	
	@UiField FlowPanel applicationsFlowPanel;
	@UiField Button settingsButton;
	@UiField ManagementConsoleControllerStyle manager;
	@UiField Label projectLabel;
	
	public DashboardPanel(ClientFactory clientFactory, String projectName) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = clientFactory.getEventBus();
		this.clientFactory = clientFactory;
		this.JSVarHandler = clientFactory.getJSVariableHandler();
		this.applications = clientFactory.getApplications();
		this.projectName = projectName;
		desc = DescriptionPanel.getInstance();
		projectLabel.setText(projectName);
		handleProjectInformation(projectName);
		//registerHandlers();
	}
	
	@UiHandler("settingsButton")
	void onSettingsButtonClick(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.SETTINGS));
	}
	
//	private void registerHandlers(){
//		
//	}

	public void handleProjectInformation(String projectName){
		Project project = clientFactory.getProjects().get(projectName);
		HashMap<String, Application> applicationsMap = clientFactory.getApplications();
		JsArrayString applicationsArray = project.getApps();
		
		for(int i = 0; i < applicationsArray.length()-1; i++) {
			final Application app = applicationsMap.get(applicationsArray.get(i));
			final FlowPanel application = new FlowPanel();
			final FocusPanel applicationLabel = new FocusPanel();
			
			Image appIcon = new Image();
			
			if(app.getIconURL().split("//").length < 2) {
				appIcon = new Image(JSVarHandler.getCommunityBaseURL() + app.getIconURL());
			} else {
				appIcon = new Image(app.getIconURL());
			}
			
			appIcon.setSize("64px", "64px");
			
			application.add(appIcon);
			application.add(new Label(app.getName()));
			
			applicationLabel.add(application);
			applicationLabel.setStyleName(manager.projectIcon());

			applicationLabel.addMouseOverHandler(new MouseOverHandler() {
				public void onMouseOver(MouseOverEvent event){
					applicationLabel.setStyleName(manager.projectIconActive());
					desc.show();
					desc.setPopupPosition(applicationLabel.getAbsoluteLeft() +
							applicationLabel.getOffsetWidth(), applicationLabel.getAbsoluteTop() - 5);
					desc.setTitle(app.getAppName());
					desc.setText(app.getDescription());
				}
			});
			applicationLabel.addMouseOutHandler(new MouseOutHandler() {
				public void onMouseOut(MouseOutEvent event){
					applicationLabel.setStyleName(manager.projectIcon());
					desc.hide();
				}
			});
			
			applicationsFlowPanel.add(applicationLabel);
		}
		
		
	}
	
	public boolean isActive(){
		return active;
	}
}
