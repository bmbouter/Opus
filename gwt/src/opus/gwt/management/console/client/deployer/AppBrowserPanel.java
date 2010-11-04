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
import java.util.Iterator;
import java.util.Set;
import java.util.Map.Entry;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.ImportAppListEvent;
import opus.gwt.management.console.client.event.ImportAppListEventHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.UpdateFeaturedListEvent;
import opus.gwt.management.console.client.event.UpdateFeaturedListEventHandler;
import opus.gwt.management.console.client.overlays.Application;
import opus.gwt.management.console.client.overlays.DjangoPackage;
import opus.gwt.management.console.client.overlays.ProjectData;
import opus.gwt.management.console.client.overlays.VersionData;
import opus.gwt.management.console.client.resources.AppBrowserCss.AppBrowserStyle;

import com.google.gwt.cell.client.CheckboxCell;
import com.google.gwt.cell.client.FieldUpdater;
import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.safehtml.shared.SafeHtmlUtils;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.cellview.client.CellTable;
import com.google.gwt.user.cellview.client.Column;
import com.google.gwt.user.cellview.client.SimplePager;
import com.google.gwt.user.cellview.client.TextColumn;
import com.google.gwt.user.cellview.client.SimplePager.TextLocation;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.LazyPanel;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.view.client.MultiSelectionModel;
import com.google.gwt.view.client.ProvidesKey;
import com.google.gwt.view.client.SelectionChangeEvent;
import com.google.gwt.view.client.SelectionModel;
import com.google.gwt.view.client.SingleSelectionModel;

public class AppBrowserPanel extends Composite {

	private static AppBrowserPanelUiBinder uiBinder = GWT.create(AppBrowserPanelUiBinder.class);
	interface AppBrowserPanelUiBinder extends UiBinder<Widget, AppBrowserPanel> {}
	
	private final String tokenURL = "/project/configuration/token/?callback=";

	private JSVariableHandler JSVarHandler;
	private int[] featured;
	private ArrayList<AppIcon> featuredIcons;
	private int navigationselection;
	private boolean featuredListLoaded;
	private boolean gridPopulationDelayed;
	private HashMap<String, Application> applicationData;
	private AppIcon currentSelection;
	private ArrayList<AppIcon> deployList;
	private EventBus eventBus;
	private ClientFactory clientFactory;
	private HashMap<String, AppIcon> IconMap;
	private HashMap<String, AppIcon> DeployListMap;
	private HashMap<String, AppIcon> FeaturedIconMap;
	
	@UiField VerticalPanel VersionInfo;
	@UiField VerticalPanel allVersionInfo;
	@UiField HTML AppInfo;
	@UiField HTML allAppInfo;
	@UiField Button AppActionButton;
	@UiField Button allAppActionButton;
	@UiField Button DeployButton;
	@UiField Button RemoveButton;
	@UiField FlowPanel DeployListFlowPanel;
	@UiField DeckPanel mainDeckPanel;
	@UiField Label allAppsLabel;
	@UiField Label featuredAppsLabel;
	@UiField Label djangoPackagesLabel;
	@UiField AppBrowserStyle style;
	@UiField FlowPanel featuredAppFlowPanel;
	@UiField FlowPanel appFlowPanel;
	@UiField LayoutPanel djangoPackagesHTMLPanel;
	@UiField HTMLPanel featuredAppsPanel;
	@UiField HTMLPanel appsPanel;
	@UiField(provided = true) DPCellTable djangoPackagesTable;
	
	public AppBrowserPanel(ClientFactory clientFactory) {
		this.clientFactory = clientFactory;
		djangoPackagesTable = new DPCellTable(clientFactory);
		initWidget(uiBinder.createAndBindUi(this));
		this.featuredListLoaded = false;
		this.gridPopulationDelayed = false;
		this.eventBus = clientFactory.getEventBus();
		this.JSVarHandler = clientFactory.getJSVariableHandler();
		registerHandlers();
		deployList = new ArrayList<AppIcon>();
		IconMap = new HashMap<String,AppIcon>();
		FeaturedIconMap = new HashMap<String,AppIcon>();
		DeployListMap = new HashMap<String,AppIcon>();
		mainDeckPanel.showWidget(0);
		navigationselection = 1;
		featuredIcons = new ArrayList<AppIcon>();
		eventBus.fireEvent(new AsyncRequestEvent("getFeatured"));
	}

	private void registerHandlers(){
		eventBus.addHandler(UpdateFeaturedListEvent.TYPE, 
			new UpdateFeaturedListEventHandler(){
				public void onUpdateFeaturedList(UpdateFeaturedListEvent event){
					populateFeaturedList(event.getFeaturedList());
				}
		});
		eventBus.addHandler(ImportAppListEvent.TYPE, 
			new ImportAppListEventHandler(){
				public void onImportAppList(ImportAppListEvent event){
					importAppList(event.getProjectData());
				}
		});
	}
	
	public void populateAppGrid(HashMap<String, Application> applications) {
		this.applicationData = applications;
		
		for (Application app : applicationData.values()){
			try {
				String name = app.getName();
				String desc =  app.getDescription();
				String email = app.getEmail();
				String author = app.getAuthor();
				int pk = app.getPk();
				String iconPath = app.getIconURL();
				String path = app.getPath();
				String type = app.getType();
				String appName = app.getAppName();
				
				if( iconPath.equals("") ){
					iconPath = "https://opus-dev.cnl.ncsu.edu/gwt/defaulticon.png";
				} else if( iconPath.split("//").length < 2  ) {
					iconPath = JSVarHandler.getCommunityBaseURL() + iconPath;
				}
				
				AppIcon appIcon = createAppIcon(name, email, author, desc, pk, iconPath, path, type, appName);					
				
				for (int j=0; j < featured.length; j++){

					//Window.alert(String.valueOf(featured.length));
					if (featured[j] == pk) {
						featuredIcons.add(appIcon);
						//featuredIcons.set(j, appIcon);
					}
				}
				
				appFlowPanel.add(appIcon);
				IconMap.put(appIcon.getAppPk(), appIcon);
				//Window.alert(appIcon.getAppPk());
			} catch (Exception e){
				//DOTO:need to handle these exceptions somehow
				//		Not sure;
			}

			
		}
		for (int j=0; j < featured.length; j++){
			AppIcon icon = IconMap.get(String.valueOf(featured[j]));
			AppIcon featuredIcon = createAppIcon(icon.getName(),icon.getEmail(), icon.getAuthor(), icon.getDescription(), Integer.valueOf(icon.getAppPk()), icon.getIcon(), icon.getPath(), icon.getType(), icon.getAppName());
			FeaturedIconMap.put(featuredIcon.getAppPk(), featuredIcon);
			featuredAppFlowPanel.add(featuredIcon);
		}
	}
	
	public AppIcon createAppIcon(String name, String email, String author, String info, int pk, String iconPath, String appPath, String type, String appName) { 
		final AppIcon icon = new AppIcon(name, email, author, iconPath, info, pk, appPath, type, appName, clientFactory);
		icon.setIconHTML("<img align='left' src='"+iconPath+"'/><b>"+name+"</b><br/>"+icon.getShortDescription());
		icon.setStyleName(style.appIcon());
		
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
		        		allAppActionButton.setText("Add to Deploy List");
			        	allAppActionButton.setStyleName(style.AppActionButton());
			        	allAppActionButton.setVisible(true);
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
		        		allAppActionButton.setText("Remove from Deploy List");
		        		allAppActionButton.setVisible(false);
		        		RemoveButton.setEnabled(true);
	        		}
        			currentSelection = icon;

		        	icon.iconPanel.setFocus(false);
		        	AppActionButton.setStyleName(style.AppActionButton());
		        	allAppActionButton.setStyleName(style.AppActionButton());
	        	}
	        }
	     });
		return icon;
	}
	
	public void setAppInfo(AppIcon icon) {
		AppInfo.setHTML("<div class='" + style.appInfoContainer() + "'><img align='left' src='" + icon.getIcon() + "' />"
				+ "<h1>" + icon.getName() + "</h1><h2>Author: " + icon.getAuthor() + "</h2>" 
				+ "<h2>Email: " + icon.getEmail() + "</h2><br />" + icon.getDescription() + "</div>");
		allAppInfo.setHTML("<div class='" + style.appInfoContainer() + "'><img align='left' src='" + icon.getIcon() + "' />"
				+ "<h1>" + icon.getName() + "</h1><h2>Author: " + icon.getAuthor() + "</h2>" 
				+ "<h2>Email: " + icon.getEmail() + "</h2><br />" + icon.getDescription() + "</div>");
		VersionInfo.clear();
		allVersionInfo.clear();
		VersionInfo.add(icon.getVersions());
		allVersionInfo.add(icon.getVersions());
	}
	
	@UiHandler("DeployButton")
	void handleNextButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.NEXT, this));
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
		djangoPackagesLabel.setStyleName(style.allAppsLabel());
		mainDeckPanel.showWidget(1);
		navigationselection = 1;
	}
	
	@UiHandler("featuredAppsLabel")
	void handleFeaturedAppsLabel(ClickEvent event){
		allAppsLabel.setStyleName(style.allAppsLabel());
		featuredAppsLabel.setStyleName(style.featuredAppsLabelActive());
		djangoPackagesLabel.setStyleName(style.allAppsLabel());
		mainDeckPanel.showWidget(0);
		navigationselection = 2;
	}
	
	@UiHandler("djangoPackagesLabel")
	void handleDjangoPackagesLabel(ClickEvent event){
		allAppsLabel.setStyleName(style.allAppsLabel());
		featuredAppsLabel.setStyleName(style.featuredAppsLabel());
		djangoPackagesLabel.setStyleName(style.allAppsLabelActive());
		mainDeckPanel.showWidget(2);
		navigationselection = 3;
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
			AppIcon iconForDeployList = createAppIcon(currentSelection.getName(), currentSelection.getEmail(), currentSelection.getAuthor(), currentSelection.getDescription(), Integer.valueOf(currentSelection.getAppPk()), currentSelection.getIcon(), currentSelection.getPath(), currentSelection.getType(), currentSelection.getAppName());
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
	
	@UiHandler("allAppActionButton")
	void handleAllAppActionButton(ClickEvent event){
		AppActionButton.click();
	}
	
	public void populateFeaturedList(JavaScriptObject jso){
		featured = new int[20];

		String[] s = jso.toString().split(",\\s*");
		featured = new int[s.length];
		//Window.alert(String.valueOf(s.length));
		for (int i=0; i<s.length; i++){
			featured[i] = Integer.valueOf(s[i]);
		}
		populateAppGrid(clientFactory.getApplications());
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
		}

	  
	  //Iterates through all icons in the deploy list and returns a list of all app paths
	  public ArrayList<String> getAppPaths() {
		  ArrayList<String> paths = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  paths.add(e.getValue().getPath());
		  }
			Iterator<DjangoPackage> dpIter = djangoPackagesTable.selectionModel.getSelectedSet().iterator();
			while( dpIter.hasNext() ){
				DjangoPackage dp = dpIter.next();
				if(dp.getType().equals("git"))
					paths.add(dp.getPath() + ".git");
				dpIter.remove();
			}
		  return paths;
	  }
	  
	  public ArrayList<String> getAppTypes() {
		  ArrayList<String> types = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  types.add(e.getValue().getType());
		  }
			Iterator<DjangoPackage> dpIter = djangoPackagesTable.selectionModel.getSelectedSet().iterator();
			while( dpIter.hasNext() ){
				types.add(dpIter.next().getType());
				dpIter.remove();
			}
			return types;
	  }
	  
	  public ArrayList<String> getApps() {
		  ArrayList<String> apps = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  apps.add(e.getValue().getName());
		  }
			Iterator<DjangoPackage> dpIter = djangoPackagesTable.selectionModel.getSelectedSet().iterator();
			while( dpIter.hasNext() ){
				apps.add(dpIter.next().getAppName());
				dpIter.remove();
			}
		  return apps;
	  }
	  
	  public ArrayList<String> getAppNames() {
		  ArrayList<String> names = new ArrayList<String>();
		  for(Entry<String,AppIcon> e : DeployListMap.entrySet()){
			  String name = e.getValue().getAppName();
			  names.add(name);
		  }
		Iterator<DjangoPackage> dpIter = djangoPackagesTable.selectionModel.getSelectedSet().iterator();
		while( dpIter.hasNext() ){
			names.add(dpIter.next().getAppName());
			dpIter.remove();
		}
		return names;
	 }
}
