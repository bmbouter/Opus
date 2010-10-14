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

package opus.gwt.management.console.client;

import java.util.HashMap;

import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.event.UpdateProjectsEvent;
import opus.gwt.management.console.client.event.UpdateProjectsEventHandler;
import opus.gwt.management.console.client.resources.PanelManagerCss.PanelManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class IconPanel extends Composite {
	
	private static IconPanelUiBinder uiBinder = GWT.create(IconPanelUiBinder.class);
	interface IconPanelUiBinder extends UiBinder<Widget, IconPanel> {}
	
	private HashMap<String, Integer> iconMap;
	private HandlerManager eventBus;
	
	@UiField ScrollPanel iconScrollPanel;
	@UiField FlowPanel projectIconsFlowPanel;
	@UiField PanelManagerStyle style;

	
	public IconPanel(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.eventBus = eventBus;
		iconMap = new HashMap<String, Integer>();
		registerHandlers();
		setupBreadCrumbs();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(UpdateProjectsEvent.TYPE, 
				new UpdateProjectsEventHandler(){
					public void onUpdateProjects(UpdateProjectsEvent event){
						for( int i=0; i < event.getProjects().length(); i++ ){
							addProjectIcon(event.getProjects().get(i).getName());
						}
					}
		});
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
	
	public void addProjectIcon(String name) {
		HTML project = new HTML();
		final String projectName = name;
		
		project.setHTML("<img src='/projectdefaulticon.png' width='64' height='64'/><br/>" + projectName);
		
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
	        	//console.mainDeckPanel.clear();
	        	//console.navigationMenuPanel.clear();
	        	//projectManager = new ProjectManagerController(eventBus); 
	        	testLabel.setStyleName(style.projectIcon());
	        }
	     });
		projectIconsFlowPanel.add(testLabel);	
		iconMap.put(name, projectIconsFlowPanel.getWidgetIndex(testLabel));
	}
	
	public void removeProjectIcon(String name){
		projectIconsFlowPanel.remove(iconMap.remove(name));
	}
}
