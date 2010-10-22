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

import opus.gwt.management.console.client.ClientFactory;
import com.google.gwt.event.shared.EventBus;
import opus.gwt.management.console.client.event.GetProjectEvent;
import opus.gwt.management.console.client.event.GetProjectEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.Project;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Widget;

public class DashboardPanel extends Composite {

	private static DashboardUiBinder uiBinder = GWT.create(DashboardUiBinder.class);
	interface DashboardUiBinder extends UiBinder<Widget, DashboardPanel> {}
	
	private JavaScriptObject appSettings;
	private boolean active;
	private EventBus eventBus;

	@UiField Button settingsButton;
	@UiField FlowPanel urlsFlowPanel;
	@UiField HTML html;
	
	public DashboardPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
	}
	
	@UiHandler("settingsButton")
	void onSettingsButtonClick(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.SETTINGS));
	}
	
	private void registerHandlers(){
		eventBus.addHandler(GetProjectEvent.TYPE,
			new GetProjectEventHandler() {
				public void onGetProject(GetProjectEvent event) {
					handleProjectInformation(event.getProject());
				}
			}
		);
	}

	public void handleProjectInformation(Project projInfo){
		html.setHTML(projInfo.getApps().get(0));
	}
	
	public boolean isActive(){
		return active;
	}
}
