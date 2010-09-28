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

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ServerCommunicator;
import opus.gwt.management.console.client.event.GetAppInfoEvent;
import opus.gwt.management.console.client.event.GetAppInfoEventHandler;
import opus.gwt.management.console.client.event.UpdateAppInfoEvent;
import opus.gwt.management.console.client.event.UpdateAppInfoEventHandler;
import opus.gwt.management.console.client.overlays.AppInfo;
import opus.gwt.management.console.client.overlays.ProjectData;
import opus.gwt.management.console.client.overlays.VersionData;
import opus.gwt.management.console.client.resources.AppBrowserCss.AppBrowserStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class AppBrowser extends Composite {

	private static AppBrowserUiBinderUiBinder uiBinder = GWT
			.create(AppBrowserUiBinderUiBinder.class);

	interface AppBrowserUiBinderUiBinder extends
			UiBinder<Widget, AppBrowser> {
	}
	
	private final String featuredURL =  "/json/featured/?a&callback=";
	private final String tokenURL = "/project/configuration/token/?callback=";

	private ServerCommunicator serverComm;
	private JSVariableHandler JSVarHandler;
	private ProjectDeployer projectDeployer;
	private FormPanel buildForm;
	private FlowPanel appFlowPanel;
	private FlowPanel featuredAppFlowPanel;
	private int[] featured;
	private ArrayList<AppIcon> featuredIcons;
	private ArrayList<AppIcon> allIcons;
	private int navigationselection;
	private boolean featuredListLoaded;
	private boolean gridPopulationDelayed;
	private JsArray<AppInfo> applicationData;
	private AppIcon currentSelection;
	private Boolean isInDeployList;
	private ArrayList<AppIcon> deployList;
	private HandlerManager eventBus;
	
	@UiField VerticalPanel VersionInfo;
	@UiField HTML AppInfo;
	@UiField Button AppActionButton;
	@UiField Button DeployButton;
	@UiField Button RemoveButton;
	@UiField FlowPanel DeployListFlowPanel;
	@UiField DeckPanel mainDeckPanel;
	@UiField Label allAppsLabel;
	@UiField Label featuredAppsLabel;
	@UiField AppBrowserStyle style;
	
	
	public AppBrowser(ProjectDeployer projectDeployer, ServerCommunicator serverComm, HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.featuredListLoaded = false;
		this.gridPopulationDelayed = false;
		this.eventBus = eventBus;
		this.projectDeployer = projectDeployer;
		JSVarHandler = new JSVariableHandler();
		this.serverComm = serverComm;
		registerEvents();
		String url = URL.encode(JSVarHandler.getRepoBaseURL()+ featuredURL);
		serverComm.getJson(url, "getFeaturedList", this);
		Window.alert("Firing GetAppinfoEvent");
		eventBus.fireEvent(new GetAppInfoEvent());
		deployList = new ArrayList<AppIcon>();
		buildForm = new FormPanel();
		setupBuildForm();
		appFlowPanel = new FlowPanel();
		featuredAppFlowPanel = new FlowPanel();
		mainDeckPanel.add(appFlowPanel);
		mainDeckPanel.add(featuredAppFlowPanel);
		mainDeckPanel.showWidget(1);
		allAppsLabel.setStyleName(style.allAppsLabel());
		featuredAppsLabel.setStyleName(style.featuredAppsLabelActive());
		navigationselection = 2;
		featuredIcons = new ArrayList<AppIcon>();
		allIcons = new ArrayList<AppIcon>();
		String token = JSVarHandler.getProjectToken();
		if (token != null) {
			this.addProject(URL.encode(JSVarHandler.getRepoBaseURL() + tokenURL.replaceAll("token", token)));
		}
	}

	private void setupBuildForm(){
		buildForm.setMethod(FormPanel.METHOD_POST);
		buildForm.getElement().setAttribute("target", "_self");
		buildForm.setVisible(false);
		buildForm.setAction(JSVarHandler.getBuildProjectURL());
	}
	
	private void registerEvents(){
		eventBus.addHandler(UpdateAppInfoEvent.TYPE, 
			new UpdateAppInfoEventHandler(){
				public void onUpdateAppInfo(UpdateAppInfoEvent event){
					populateAppGrid(event.getAppInfo());
				}
		});
	}
	
	public void populateAppGrid(JsArray <AppInfo> applications) {
		this.applicationData = applications;
		if(this.featuredListLoaded){
			String innerHTML = "";
			for (int i=0; i<applications.length(); i++){
				try {
					String name = applications.get(i).getName();
					String desc =  applications.get(i).getDescription();
					String email = applications.get(i).getEmail();
					String author = applications.get(i).getAuthor();
					int pk = applications.get(i).getPk();
					String iconPath = applications.get(i).getIconURL();
					String path = applications.get(i).getPath();
					
					if( iconPath.equals("") ){
						iconPath = "https://opus-dev.cnl.ncsu.edu/gwt/defaulticon.png";
					}
					AppIcon appIcon = createAppIcon(name, email, author, desc, pk, iconPath, path);
	
					for (int j=0; j < featured.length; j++){
	
						//Window.alert(String.valueOf(featured.length));
						if (featured[j] == pk) {
							featuredIcons.add(appIcon);
							//featuredIcons.set(j, appIcon);
						}
					}
					appFlowPanel.add(appIcon);
					allIcons.add(appIcon);
				} catch (Exception e){
					//DOTO:need to handle these exceptions somehow
					//		Not sure;
				}

				
			}
	
			handleFeaturedAppsLabelFunction();
			String token = JSVarHandler.getProjectToken();
			if (token != null) {
				String url =URL.encode(JSVarHandler.getRepoBaseURL() + tokenURL.replaceAll("token", token));
				//Window.alert(url);
				serverComm.getJson(url,  "importAppList", this);
			}
		} else {
			this.gridPopulationDelayed = true;
		}
		
	}
	
	public void setAppInfo(AppIcon icon) {
		AppInfo.setHTML("<div class='" + style.appInfoContainer() + "'><img align='left' src='" + icon.getIcon() + "' />"
				+ "<h1>" + icon.getName() + "</h1><h2>Author: " + icon.getAuthor() + "</h2>" 
				+ "<h2>Email: " + icon.getEmail() + "</h2><br />" + icon.getDescription() + "</div>");
		VersionInfo.clear();
		VersionInfo.add(icon.getVersions());
		//AppInfo.setHTML(description + versions.toString());
		//Window.alert(versions.toString());
		
	}
	
	public AppIcon createAppIcon(String name, String email, String author, String info, int pk, String iconPath, String appPath) { 
		final AppIcon icon = new AppIcon(name, email, author, iconPath, info, pk, appPath);
		icon.setIconHTML("<img align='left' src='"+iconPath+"'/><b>"+name+"</b><br/>"+icon.getShortDescription());
		icon.setStyleName(style.appIcon());
		
		final String versionsURL = URL.encode(JSVarHandler.getRepoBaseURL() + "/json/application/" + String.valueOf(pk) + "/versions/?a") + "&callback=";
		
		serverComm.getJson(versionsURL,  "getVersionInfo", icon);
		
		icon.iconPanel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	//if the icon is already selected don't do anything
	        	//if the icon is selected and it is in AppList, make style appIconActive and set icon as currentSelection and display info, change previous selection back to inactive
	        	//if the icon is selected and it is in the DeployList, make style appIconSmallActive and set icon as currentSelection and display info, change previous selection to inactive
	        	if(currentSelection != icon) {
	        		if (currentSelection != null) {
	        			if (deployList.contains(currentSelection)) {
	        				currentSelection.setStyleName(style.appIconSmall());
	        				RemoveButton.setEnabled(true);
	        			} else {
	        				currentSelection.setStyleName(style.appIcon());
	        				RemoveButton.setEnabled(false);
	        			}
	        		}
	        		if (deployList.contains(icon) == false) {
	        			icon.setStyleName(style.appIconActive());
	        			currentSelection = icon;
	        			//setAppInfo(icon.getDescription(),icon.getVersions());
	        			setAppInfo(icon);
		        		AppActionButton.setText("Add to Deploy List");
			        	AppActionButton.setStyleName(style.AppActionButton());
			        	AppActionButton.setVisible(true);
		        		RemoveButton.setEnabled(false);
	        		} else {
	        			icon.setStyleName(style.appIconSmallActive());
	        			currentSelection = icon;
	        			//setAppInfo(icon.getDescription(), icon.getVersions());
	        			setAppInfo(icon);
		        		AppActionButton.setText("Remove from Deploy List");
		        		AppActionButton.setVisible(false);
		        		RemoveButton.setEnabled(true);
	        		}
		        	icon.iconPanel.setFocus(false);
		        	AppActionButton.setStyleName(style.AppActionButton());
	        	}
	        }
	     });
		return icon;
	}
	
	@UiHandler("DeployButton")
	void handleNextButton(ClickEvent event){
		projectDeployer.showNextPanel(this);
	}
	
	@UiHandler("RemoveButton")
	void handleRemoveButton(ClickEvent event){
		AppActionButton.click();
		if(deployList.contains(currentSelection)) {
			RemoveButton.setEnabled(true);
		} else {
			RemoveButton.setEnabled(false);
		}
	}
	/*
	@UiHandler("DeployButton")
	void handleDeployButton(ClickEvent event){	
		  if (deployList.size() > 0) {
			  VerticalPanel formContainerPanel = new VerticalPanel();
			  this.buildForm.add(formContainerPanel);
			  ListBox versions = new ListBox();
			  versions.setName("versions");
			  formContainerPanel.add(versions);
			  //check how many were manually added
			  int count = 0;
			  for(int i = 0; i < deployList.size(); i++){
				  versions.addItem(deployList.get(i).getPk());
			  }
			  TextBox name = new TextBox();
			  name.setName("name");
			  formContainerPanel.add(name);
			  Hidden numApps = new Hidden();
			  numApps.setName("form-TOTAL_FORMS");
			  numApps.setValue(String.valueOf(count));
			  formContainerPanel.add(numApps);
			  Hidden numInitialForms = new Hidden();
			  numInitialForms.setName("form-INITIAL_FORMS");
			  numInitialForms.setValue("0");
			  Hidden numMaxForms = new Hidden();
			  numMaxForms.setName("form-MAX_NUM_FORMS");
			  formContainerPanel.add(numInitialForms);
			  formContainerPanel.add(numMaxForms);
			 
			  formContainerPanel.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
			  
			  RootPanel.get().add(buildForm);
			  buildForm.submit();
			  //Window.alert(buildForm.getMethod());
		  }
	}
	*/
	@UiHandler("allAppsLabel")
	void handleAllAppsLabel(ClickEvent event){
		allAppsLabel.setStyleName(style.allAppsLabelActive());
		featuredAppsLabel.setStyleName(style.featuredAppsLabel());
		mainDeckPanel.showWidget(0);
		navigationselection = 1;
		for (int i=0; i<featuredIcons.size(); i++){
			appFlowPanel.add(featuredIcons.get(i));
		}
	}
	
	@UiHandler("featuredAppsLabel")
	void handleFeaturedAppsLabel(ClickEvent event){
		handleFeaturedAppsLabelFunction();
	}
	
	public void handleFeaturedAppsLabelFunction(){
		allAppsLabel.setStyleName(style.allAppsLabel());
		featuredAppsLabel.setStyleName(style.featuredAppsLabelActive());
		mainDeckPanel.showWidget(1);
		navigationselection = 2;
		for (int i=0; i<featuredIcons.size(); i++){
			featuredAppFlowPanel.add(featuredIcons.get(i));
		}
	}
	
	@UiHandler("AppActionButton")
	void handleAppActionButton(ClickEvent event){
		//If the icon is in the AppList, change style to appIconSmallActive, change html to icon and name, add to DeployList and DeployListFlowPanel, change button text
		//If the icon is in the DeployList, change style to appIconActive, change html to icon, name, short description, remove from DeployList, add to AppListFlowPanel, change button text
		
		if (deployList.contains(currentSelection)){
			currentSelection.setStyleName(style.appIconActive());
			currentSelection.setIconHTML("<img align='left' src='"+currentSelection.getIcon()+"'/><b>"+currentSelection.getName()+"</b><br/>"+currentSelection.getShortDescription());
			deployList.remove(currentSelection);
			appFlowPanel.add(currentSelection);
			//Check which panel is on display. Check the list of featured. If this one is featured, add to featuredIcons.

			appFlowPanel.add(currentSelection);
			
			for(int i=0; i<featured.length; i++){
				if (featured[i] == Integer.valueOf(currentSelection.getAppPk())){
					featuredIcons.add(currentSelection);
					if(navigationselection == 2) {
						featuredAppFlowPanel.add(currentSelection);
					}
				}
			}
			AppActionButton.setText("Add to Deploy List");
			AppActionButton.setVisible(true);
		} else {
			currentSelection.setStyleName(style.appIconSmallActive());
			currentSelection.setIconHTML("<img src='"+currentSelection.getIcon()+"'><br/>"+currentSelection.getName());
			deployList.add(currentSelection);
			DeployListFlowPanel.add(currentSelection);
			//Remove from featuredIcons if it is one.
			featuredIcons.remove(currentSelection);
			AppActionButton.setText("Remove from Deploy List");
			AppActionButton.setVisible(false);
			RemoveButton.setEnabled(true);
		}
		
		if(deployList.size() > 0) {
			DeployButton.setEnabled(true);
		} else {
			DeployButton.setEnabled(false);
		}
	}
	
	public void populateFeaturedList(JavaScriptObject jso){
		featured = new int[20];
		//comment
		String[] s = jso.toString().split(",\\s*");
		for (int i=0; i<s.length; i++){
			featured[i] = Integer.valueOf(s[i]);
		}
		this.featuredListLoaded = true;
		if(this.gridPopulationDelayed) {
			this.populateAppGrid(this.applicationData);
		}
	}
	
	  public void addProject(String url){
		  serverComm.getJson(url,  "importAppList", this);
	  }
	  
	  public void importAppList(JsArray<ProjectData> projectData) {
		  
		  JsArray<VersionData>versions = projectData.get(0).getVersions();
		  //Window.alert("got inside importAppList");

		  deployList.clear();
		  for (int i=0; i < versions.length(); i++){
			  for(int j=0; j<allIcons.size(); j++){
				  if (allIcons.get(j).getAppPk().equals(versions.get(i).getAppPk())){
					  AppIcon match = allIcons.get(j);
					  match.setSelectedVersion(Integer.valueOf(versions.get(i).getVersionPk()));
					  match.setStyleName(style.appIconSmall());
					  match.setIconHTML("<img src='"+match.getIcon()+"'><br/>"+match.getName());
					  deployList.add(match);
					  DeployListFlowPanel.add(match);
					  //Remove from featuredIcons if it is one.
					  featuredIcons.remove(match);
					  AppActionButton.setText("Remove from Deploy List");
					  AppActionButton.setVisible(false);
					  RemoveButton.setEnabled(false);
					  j = allIcons.size();
				  }
			  }
			//  this.createAppIcon(communityApps.get(i).getName(), communityApps.get(i).getInfo(), communityApps.get(i).getPk())
			//  this.addApp(communityApps.get(i).getName(), communityApps.get(i).getPath(), communityApps.get(i).getType());
		  }

	  }
	  
	  public ArrayList<String> getAppPaths() {
		  ArrayList<String> paths = new ArrayList<String>();
		  for (int i=0; i<deployList.size(); i++){
			  paths.add(deployList.get(i).getPath());
		  }
		  return paths;
	  }
	  
	  public ArrayList<String> getAppTypes() {
		  ArrayList<String> types = new ArrayList<String>();
		  for (int i=0; i < deployList.size(); i++){
			  types.add(deployList.get(i).getType());
		  }
		  return types;
	  }
	  
	  public ArrayList<String> getApps() {
		  ArrayList<String> apps = new ArrayList<String>();
		  for (int i=0; i<deployList.size(); i++){
			  apps.add(deployList.get(i).getName());
		  }
		  return apps;
	  }
}
