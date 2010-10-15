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

package opus.gwt.management.console.client.deployer;

import java.util.ArrayList;

import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.DeployProjectEvent;
import opus.gwt.management.console.client.event.DeployProjectEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.resources.ProjectDeployerCss.ProjectDeployerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;


public class ProjectDeployerController extends Composite {
	
	private static applicationDeployerUiBinder uiBinder = GWT.create(applicationDeployerUiBinder.class);
	interface applicationDeployerUiBinder extends UiBinder<Widget, ProjectDeployerController> {}
		
	private final String deploymentURL =  "/deployments/projectName/";
		
	private ProjectOptionsPanel projectOptionsPanel;
	private DatabaseOptionsPanel databaseOptionsPanel;
	private DeploymentOptionsPanel deploymentOptionsPanel;
	private AppBrowserPanel appBrowserPanel;
	private HandlerManager eventBus;
	private FormPanel deployerForm;
	private String createdProjectName;
	private PopupPanel loadingPopup;
	private Image loadingImage;
		
	@UiField DeckPanel deployerDeckPanel;
	@UiField ProjectDeployerStyle style;
	
	public ProjectDeployerController(HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		createdProjectName = "";
		this.eventBus = eventBus;
		loadingPopup = new PopupPanel(false, true);
		loadingImage = new Image("/loadinfo.net.gif");
		//loadingImage.setStyleName(style.loadingImage());
		loadingPopup.add(loadingImage);
		this.deployerForm = new FormPanel();
		this.appBrowserPanel = new AppBrowserPanel(eventBus);
		this.projectOptionsPanel = new ProjectOptionsPanel(eventBus);
		this.databaseOptionsPanel = new DatabaseOptionsPanel(eventBus);
		this.deploymentOptionsPanel = new DeploymentOptionsPanel(eventBus);
		setupdeployerDeckPanel();
		registerEvents();
		setupBreadCrumbs();
		setupDeployerForm();
	}
	
	private void setupdeployerDeckPanel(){
		deployerDeckPanel.add(appBrowserPanel);
		deployerDeckPanel.add(projectOptionsPanel);
		deployerDeckPanel.add(databaseOptionsPanel);
		deployerDeckPanel.add(deploymentOptionsPanel);
		appBrowserPanel.setTitle("Application Browser");
		projectOptionsPanel.setTitle("Project Options");
		databaseOptionsPanel.setTitle("Database Options");
		deploymentOptionsPanel.setTitle("Deployment Options");
		deployerDeckPanel.showWidget(0);
		appBrowserPanel.setHeight("");
		appBrowserPanel.setWidth("");
	}
	
	private void setupBreadCrumbs(){
		String[] crumbs = {appBrowserPanel.getTitle(), projectOptionsPanel.getTitle(), databaseOptionsPanel.getTitle(), deploymentOptionsPanel.getTitle()};
		eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_CRUMBS, crumbs));
	}
	
	private void setupDeployerForm(){
		deployerForm.clear();
		deployerForm.setMethod(FormPanel.METHOD_POST);
		deployerForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		    public void onSubmitComplete(SubmitCompleteEvent event) {
		    	//if( event.getResults().equals("success") ){
		    		loadingPopup.hide();
		    		//eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.DASHBOARD, createdProjectName));
		    		ErrorPanel ep = new ErrorPanel(eventBus);
		    		ep.errorHTML.setHTML(event.getResults());
		    		deployerDeckPanel.add(ep);
		    		deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(ep));
		    	/*} else {
		    		ErrorPanel ep = new ErrorPanel(eventBus);
		    		deployerDeckPanel.add(ep);
		    		deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(ep));
		    	}*/
		     }});
	}
	
	private void registerEvents(){
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
			new PanelTransitionEventHandler(){
				public void onPanelTransition(PanelTransitionEvent event){
					if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.NEXT ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) + 1);
						eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
						setFocus(panel);
					} else if( event.getTransitionType() == PanelTransitionEvent.TransitionTypes.PREVIOUS ){
						Widget panel =  event.getPanel();
						deployerDeckPanel.showWidget(deployerDeckPanel.getWidgetIndex(panel) - 1);
						eventBus.fireEvent(new BreadCrumbEvent(BreadCrumbEvent.Action.SET_ACTIVE, deployerDeckPanel.getWidget(deployerDeckPanel.getVisibleWidget()).getTitle()));
					}
		}});
		eventBus.addHandler(DeployProjectEvent.TYPE, 
				new DeployProjectEventHandler(){
					public void onDeployProject(DeployProjectEvent event){
						deployProject();
					}
		});
	}
	
	public void setFocus(Widget panel){
		if( panel.getClass().equals(databaseOptionsPanel.getClass()) ){
			deploymentOptionsPanel.setFocus();
		} else if( panel.getClass().equals(appBrowserPanel.getClass()) ){
			projectOptionsPanel.setFocus();
		} else if( panel.getClass().equals(projectOptionsPanel.getClass()) ){
			databaseOptionsPanel.setFocus();
		}
	}
	 
	private void deployProject(){
		deployerForm.clear();
		createdProjectName = deploymentOptionsPanel.getProjectName();
		deployerForm.setAction(deploymentURL.replaceAll("projectName", deploymentOptionsPanel.getProjectName())); 
  
		VerticalPanel formContainerPanel = new VerticalPanel();
		this.deployerForm.add(formContainerPanel);
  
		ArrayList<String> paths = appBrowserPanel.getAppPaths();
		ArrayList<String> apptypes = appBrowserPanel.getAppTypes();
		Hidden numApps = new Hidden();
		numApps.setName("form-TOTAL_FORMS");
		numApps.setValue(String.valueOf(paths.size()));
		formContainerPanel.add(numApps);
		
		Hidden numInitialForms = new Hidden();
		numInitialForms.setName("form-INITIAL_FORMS");
		numInitialForms.setValue("0");
		formContainerPanel.add(numInitialForms);
		
		Hidden numMaxForms = new Hidden();
		numMaxForms.setName("form-MAX_NUM_FORMS");
		formContainerPanel.add(numMaxForms);
		
		for(int i=0; i < paths.size(); i++) {
			RadioButton pathtype = new RadioButton("form-" + i + "-apptype");
			pathtype.setFormValue(apptypes.get(i));
			pathtype.setValue(true);
			TextBox path = new TextBox();
			path.setName("form-" + i +"-apppath");
			path.setValue(paths.get(i));
			formContainerPanel.add(pathtype);
			formContainerPanel.add(path);
		}
	  
		formContainerPanel.add(deploymentOptionsPanel);
		formContainerPanel.add(projectOptionsPanel);
		formContainerPanel.add(databaseOptionsPanel);
	 
		//Add csrf-token
		formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
		deployerDeckPanel.add(deployerForm);
		deployerForm.submit();
		loadingPopup.setGlassEnabled(true);
		loadingPopup.setGlassStyleName(style.loadingGlass());
		loadingPopup.show();
		int left = ( Window.getClientWidth() / 2 ) - (loadingImage.getOffsetWidth() / 2);
		int top = ( Window.getClientHeight() / 2) -  (loadingImage.getOffsetHeight() / 2);
		loadingPopup.setSize(Integer.toString(Window.getClientWidth()), Integer.toString(Window.getClientHeight()));
		loadingPopup.setPopupPosition(left, top);
		loadingPopup.show();
	}
}
