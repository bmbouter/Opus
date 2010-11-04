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
import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.resources.ManagementConsoleControllerResources.ManagementConsoleControllerStyle;
import opus.gwt.management.console.client.resources.images.OpusImages;
import opus.gwt.management.console.client.tools.DescriptionPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JsArrayString;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class IconPanel extends Composite {
	
	private static IconPanelUiBinder uiBinder = GWT.create(IconPanelUiBinder.class);
	interface IconPanelUiBinder extends UiBinder<Widget, IconPanel> {}
	
	private HashMap<String, Integer> iconMap;
	private EventBus eventBus;
	private ClientFactory clientFactory;
	private DescriptionPanel desc;
	
	@UiField ScrollPanel iconScrollPanel;
	@UiField FlowPanel projectIconsFlowPanel;
	@UiField ManagementConsoleControllerStyle style;
	@UiField OpusImages res;
	
	public IconPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = clientFactory.getEventBus();
		this.clientFactory = clientFactory;
		iconMap = new HashMap<String, Integer>();
		desc = DescriptionPanel.getInstance();
		registerHandlers();
		setupBreadCrumbs();
		setAppDescPanelInitialState();
		handleProjects();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.PROJECTS ){
						setupBreadCrumbs();
					}
				}
		});
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {"Projects"};
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_CRUMBS, crumbs));
	}
	
	private void handleProjects() {
		iconMap.clear();
		projectIconsFlowPanel.clear();
		
		HashMap<String, Project> projects = clientFactory.getProjects();
		
		for(Project project : projects.values()){
			addProjectIcon(project);
		}
	}
	
	public void addProjectIcon(Project project) {
		FlowPanel projectPanel = new FlowPanel();
		
		JsArrayString appStrings = project.getApps();
		String description = "";
		
		for(int i = 0; i < appStrings.length(); i++) {
			if(i == appStrings.length() - 1)
				description += appStrings.get(i);
			else
				description += appStrings.get(i) + ", ";
		}
		
		final String projectName = project.getName();
		final String appNames = description;
		
		Image projectImg = new Image(res.projectdefaulticon2().getUrl());
		projectImg.setPixelSize(64, 64);
		
		projectPanel.add(projectImg);
		projectPanel.add(new Label(projectName));
		
		final FocusPanel testLabel = new FocusPanel();
		testLabel.add(projectPanel);
		testLabel.setStyleName(style.projectIcon());
		testLabel.addMouseOverHandler(new MouseOverHandler(){
			public void onMouseOver(MouseOverEvent event){
				testLabel.setStyleName(style.projectIconActive());
				desc.show();
				desc.setPopupPosition(testLabel.getAbsoluteLeft() +
						testLabel.getOffsetWidth(), testLabel.getAbsoluteTop() - 5);
				desc.setTitle("Applications");
				desc.setText(appNames);
			}
		});
		testLabel.addMouseOutHandler(new MouseOutHandler(){
			public void onMouseOut(MouseOutEvent event){
				testLabel.setStyleName(style.projectIcon());
				desc.hide();
			}
		});
		testLabel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	testLabel.setStyleName(style.projectIcon());
	        	eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DASHBOARD, projectName));
	        }
	     });
		
		projectIconsFlowPanel.add(testLabel);	
		iconMap.put(project.getName(), projectIconsFlowPanel.getWidgetIndex(testLabel));
	}
	
	public void removeProjectIcon(String name){
		projectIconsFlowPanel.remove(iconMap.remove(name));
	}
	
	private void setAppDescPanelInitialState() {
		desc.setVisible(false);
		desc.show();
		desc.setPopupPosition(-100, -100);
		desc.hide();
		desc.setVisible(true);
	}
}
