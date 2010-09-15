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
import java.util.HashMap;
import java.util.Map.Entry;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ServerCommunicator;
import opus.gwt.management.console.client.overlays.AppData;
import opus.gwt.management.console.client.overlays.ProjectData;
import opus.gwt.management.console.client.overlays.VersionData;
import opus.gwt.management.console.client.resources.AppBrowserCss;
import opus.gwt.management.console.client.resources.AppBrowserCss.AppBrowserStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
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
import com.google.gwt.user.client.ui.HTMLPanel;
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
	private final String appListURL = "/json/search/application/?a&callback=";
	private final String tokenURL = "/project/configuration/token/?callback=";
	private final String versionURL = "/json/application/pk/versions/?callback=";

	private ServerCommunicator communicator;
	private JSVariableHandler JSVarHandler;
	private ProjectDeployer appDeployer;
	private FormPanel buildForm;
	private FlowPanel appFlowPanel;
	private FlowPanel featuredAppFlowPanel;
	private int[] featured;
	private ArrayList<AppIcon> featuredIcons;
	private int navigationselection;
	private boolean featuredListLoaded;
	private boolean gridPopulationDelayed;
	private JsArray<AppData> applicationData;
	private AppIcon currentSelection;
	private HashMap<String,AppIcon> IconMap;
	private HashMap<String,AppIcon> DeployListMap;
	private HashMap<String,AppIcon> FeaturedIconMap;
	
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
	
	
	public AppBrowser(ProjectDeployer appDeployer, ServerCommunicator jsonCom) {
		this.featuredListLoaded = false;
		this.gridPopulationDelayed = false;
		initWidget(uiBinder.createAndBindUi(this));
		this.appDeployer = appDeployer;
		JSVarHandler = new JSVariableHandler();
		communicator = jsonCom;
		String url = URL.encode(JSVarHandler.getRepoBaseURL()+ featuredURL);
		communicator.getJson(url, communicator, "getFeaturedList", this);
		url = URL.encode(JSVarHandler.getRepoBaseURL() + appListURL);
		communicator.getJson(url, communicator, "getAppInfo", this);
		buildForm = new FormPanel();
		IconMap = new HashMap<String,AppIcon>();
		FeaturedIconMap = new HashMap<String,AppIcon>();
		DeployListMap = new HashMap<String,AppIcon>();
		appFlowPanel = new FlowPanel();
		featuredAppFlowPanel = new FlowPanel();
		mainDeckPanel.add(appFlowPanel);
		mainDeckPanel.add(featuredAppFlowPanel);
		mainDeckPanel.showWidget(1);
		allAppsLabel.setStyleName(style.allAppsLabel());
		featuredAppsLabel.setStyleName(style.featuredAppsLabelActive());
		navigationselection = 2;
		featuredIcons = new ArrayList<AppIcon>();
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
	
	public final native JsArray<AppData> asArrayOfAppData(JavaScriptObject jso) /*-{
	    return jso;
	}-*/;
	
	public void populateAppGrid(JsArray <AppData> applications) {
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
					String type = applications.get(i).getType();
					
					if( iconPath.equals("") ){
						iconPath = "https://opus-dev.cnl.ncsu.edu/gwt/defaulticon.png";
					}
					AppIcon appIcon = createAppIcon(name, email, author, desc, pk, iconPath, path, type);
					appFlowPanel.add(appIcon);
					IconMap.put(appIcon.getAppPk(), appIcon);
					//Window.alert(appIcon.getAppPk());
				} catch (Exception e){
					//DOTO:need to handle these exceptions somehow
					//		Not sure;
				}

				
			}
			for (int j=0; j < featured.length; j++){
				//Window.alert(String.valueOf(featured[j]));

				AppIcon icon = IconMap.get(String.valueOf(featured[j]));
				AppIcon featuredIcon = createAppIcon(icon.getName(),icon.getEmail(), icon.getAuthor(), icon.getDescription(), Integer.valueOf(icon.getAppPk()), icon.getIcon(), icon.getPath(), icon.getType());
				FeaturedIconMap.put(featuredIcon.getAppPk(), featuredIcon);

				featuredAppFlowPanel.add(featuredIcon);

			}
			handleFeaturedAppsLabelFunction();
			String token = JSVarHandler.getProjectToken();
			if (token != null) {
				String url =URL.encode(JSVarHandler.getRepoBaseURL() + tokenURL.replaceAll("token", token));
				//Window.alert(url);
				communicator.getJson(url, communicator, "importAppList", this);
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
	
	public AppIcon createAppIcon(String name, String email, String author, String info, int pk, String iconPath, String appPath, String type) { 
		final AppIcon icon = new AppIcon(name, email, author, iconPath, info, pk, appPath, type);
		icon.setIconHTML("<img align='left' src='"+iconPath+"'/><b>"+name+"</b><br/>"+icon.getShortDescription());
		icon.setStyleName(style.appIcon());
		
		final String versionsURL = URL.encode(JSVarHandler.getRepoBaseURL() + versionURL.replaceAll("pk", String.valueOf(pk)));
		
		communicator.getJson(versionsURL, communicator, "getVersionInfo", icon);
		
		icon.iconPanel.addClickHandler(new ClickHandler() {
	        public void onClick(ClickEvent event) {
	        	//if the icon is already selected don't do anything
	        	//if the icon is selected and it is in AppList, make style appIconActive and set icon as currentSelection and display info, change previous selection back to inactive
	        	//if the icon is selected and it is in the DeployList, make style appIconSmallActive and set icon as currentSelection and display info, change previous selection to inactive
	        	if(currentSelection != icon) {
	        		if (currentSelection != null) {
	        			IconMap.get(currentSelection.getAppPk()).setStyleName(style.appIcon());
	        			if (DeployListMap.containsKey((currentSelection.getAppPk()))) {
	        				DeployListMap.get(currentSelection.getAppPk()).setStyleName(style.appIconSmall());
	        				RemoveButton.setEnabled(true);
	        			} else {
	        				RemoveButton.setEnabled(false);
	        			}
	        			if (FeaturedIconMap.containsKey(currentSelection.getAppPk())){
        					FeaturedIconMap.get(currentSelection.getAppPk()).setStyleName(style.appIcon());
        				}
	        		}
	        		/*if (deployListReplacements.contains(icon)){
	        			int index = deployListReplacements.indexOf(icon);
	        			deployList.get(index).setStyleName(style.appIconSmallActive());
	        		}*/
	        		if (DeployListMap.containsKey(icon.getAppPk()) == false) {
	        			IconMap.get(icon.getAppPk()).setStyleName(style.appIconActive());

	        			if (FeaturedIconMap.containsKey(icon.getAppPk())){
        					FeaturedIconMap.get(icon.getAppPk()).setStyleName(style.appIconActive());
        				}
	        			setAppInfo(icon);
		        		AppActionButton.setText("Add to Deploy List");
			        	AppActionButton.setStyleName(style.AppActionButton());
			        	AppActionButton.setVisible(true);
		        		RemoveButton.setEnabled(false);
	        		} else {
	        			DeployListMap.get(icon.getAppPk()).setStyleName(style.appIconSmallActive());
	        			IconMap.get(icon.getAppPk()).setStyleName(style.appIconActive());
	        			if (FeaturedIconMap.containsKey(icon.getAppPk())){
	        				FeaturedIconMap.get(icon.getAppPk()).setStyleName(style.appIconActive());
	        			}
	        			currentSelection = icon;
	        			//setAppInfo(icon.getDescription(), icon.getVersions());
	        			setAppInfo(icon);
		        		AppActionButton.setText("Remove from Deploy List");
		        		AppActionButton.setVisible(false);
		        		RemoveButton.setEnabled(true);
	        		}
        			currentSelection = icon;

		        	icon.iconPanel.setFocus(false);
		        	AppActionButton.setStyleName(style.AppActionButton());
	        	}
	        }
	     });
		return icon;
	}
	
	@UiHandler("DeployButton")
	void handleNextButton(ClickEvent event){
		appDeployer.handleProjectOptionsLabel();
	}
	
	@UiHandler("RemoveButton")
	void handleRemoveButton(ClickEvent event){
		AppActionButton.click();
		if(DeployListMap.containsKey(currentSelection.getAppPk())) {
			RemoveButton.setEnabled(true);
		} else {
			RemoveButton.setEnabled(false);
		}
	}

	@UiHandler("allAppsLabel")
	void handleAllAppsLabel(ClickEvent event){
		allAppsLabel.setStyleName(style.allAppsLabelActive());
		featuredAppsLabel.setStyleName(style.featuredAppsLabel());
		mainDeckPanel.showWidget(0);
		navigationselection = 1;
	//	for (int i=0; i<featuredIcons.size(); i++){
	//		appFlowPanel.add(featuredIcons.get(i));
	//	}
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
		//for (int i=0; i<featuredIcons.size(); i++){
			//featuredAppFlowPanel.add(featuredIcons.get(i));
		//}
	}
	
	@UiHandler("AppActionButton")
	void handleAppActionButton(ClickEvent event){

		if (DeployListMap.containsKey(currentSelection.getAppPk())){
			DeployListFlowPanel.remove(DeployListMap.get(currentSelection.getAppPk()));
			DeployListMap.remove(currentSelection.getAppPk());
			AppActionButton.setText("Add to Deploy List");
			AppActionButton.setVisible(true);
		} else {
			
			//create new icon and add it to the deploy list
			AppIcon iconForDeployList = createAppIcon(currentSelection.getName(), currentSelection.getEmail(), currentSelection.getAuthor(), currentSelection.getDescription(), Integer.valueOf(currentSelection.getAppPk()), currentSelection.getIcon(), currentSelection.getPath(), currentSelection.getType());
			iconForDeployList.setStyleName(style.appIconSmallActive());
			iconForDeployList.setIconHTML("<img src='"+currentSelection.getIcon()+"'><br/>"+currentSelection.getName());
			DeployListMap.put(iconForDeployList.getAppPk(),iconForDeployList);
			DeployListFlowPanel.add(iconForDeployList);
			//Remove from featuredIcons if it is one.
			AppActionButton.setText("Remove from Deploy List");
			AppActionButton.setVisible(false);
			RemoveButton.setEnabled(true);

		}
		
		if(DeployListMap.size() > 0) {
			DeployButton.setEnabled(true);
		} else {
			DeployButton.setEnabled(false);
		}
	}
	
	public void populateFeaturedList(JavaScriptObject jso){
		
		//comment
		String[] s = jso.toString().split(",\\s*");
		featured = new int[s.length];
		//Window.alert(String.valueOf(s.length));
		for (int i=0; i<s.length; i++){
			featured[i] = Integer.valueOf(s[i]);
		}
		this.featuredListLoaded = true;
		if(this.gridPopulationDelayed) {
			this.populateAppGrid(this.applicationData);
		}
	}
	
	  public void addProject(String url){
		  communicator.getJson(url, communicator, "importAppList", this);
	  }
	  
	  public void importAppList(JsArray<ProjectData> projectData) {
		  
		  JsArray<VersionData>versions = projectData.get(0).getVersions();
		  //Window.alert("got inside importAppList");

		  DeployListMap.clear();
		  for (int i=0; i < versions.length(); i++){
			  for (Entry<String,AppIcon> e : IconMap.entrySet())
				  if (e.getValue().getAppPk().equals(versions.get(i).getAppPk())){
					  AppIcon match = e.getValue();
					  match.setSelectedVersion(Integer.valueOf(versions.get(i).getVersionPk()));
					  match.setStyleName(style.appIconSmall());
					  match.setIconHTML("<img src='"+match.getIcon()+"'><br/>"+match.getName());
					  DeployListMap.put(match.getAppPk(),match);
					  DeployListFlowPanel.add(match);
					  AppActionButton.setText("Remove from Deploy List");
					  AppActionButton.setVisible(false);
					  RemoveButton.setEnabled(false);
					  break;
				  }
			  }
			//  this.createAppIcon(communityApps.get(i).getName(), communityApps.get(i).getInfo(), communityApps.get(i).getPk())
			//  this.addApp(communityApps.get(i).getName(), communityApps.get(i).getPath(), communityApps.get(i).getType());
		 }

	  
	  //Iterates through all icons in the deploy list and returns a list of all app paths
	  public ArrayList<String> getAppPaths() {
		  ArrayList<String> paths = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  paths.add(e.getValue().getPath());
		  }
		  return paths;
	  }
	  
	  public ArrayList<String> getAppTypes() {
		  ArrayList<String> types = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  types.add(e.getValue().getType());
		  }
		  return types;
	  }
	  
	  public ArrayList<String> getApps() {
		  ArrayList<String> apps = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  apps.add(e.getValue().getName());
		  }
		  return apps;
	  }
	  
	  public ArrayList<String> getAppNames() {
		  ArrayList<String> names = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  String name = e.getValue().getPath();
			  String[] name_split = name.split("/");
			  name = name_split[name_split.length - 1].split(".git")[0];
			  Window.alert(name);
			  names.add(name);
		  }
		  return names;
	  }
	  
	  public final native JsArray<ProjectData> asArrayOfProjectData(JavaScriptObject jso) /*-{
		  return jso;
	  }-*/;
}
