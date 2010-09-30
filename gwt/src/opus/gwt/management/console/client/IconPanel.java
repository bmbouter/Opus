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

import opus.gwt.management.console.client.dashboard.ProjectManager;
import opus.gwt.management.console.client.resources.ManagementConsoleCss.ManagementConsoleStyle;

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
	
	private static IconPanelUiBinder uiBinder = GWT
			.create(IconPanelUiBinder.class);

	interface IconPanelUiBinder extends UiBinder<Widget, IconPanel> {
	}
	
	private PanelManager console;
	private ProjectManager projectManager;
	private HashMap<String, Integer> iconMap;
	private HandlerManager eventBus;
	
	@UiField ScrollPanel iconScrollPanel;
	@UiField FlowPanel projectIconsFlowPanel;
	@UiField ManagementConsoleStyle style;

	
	public IconPanel(PanelManager console, HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.console = console;
		this.eventBus = eventBus;
		iconMap = new HashMap<String, Integer>();
	}
	
	public void addProjectIcon(String name) {
		HTML project = new HTML();
		project.setHTML("<img src='/gwt/projectdefaulticon.png' width='64' height='64'/><br/>"+name);
		
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
	        	//console.navigationMenuPanel.clear();
	        	projectManager = new ProjectManager(eventBus); 
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
