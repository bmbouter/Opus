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
import opus.gwt.management.console.client.overlays.AppData;
import opus.gwt.management.console.client.overlays.DependencyData;
import opus.gwt.management.console.client.overlays.ModelProperties;
import opus.gwt.management.console.client.overlays.ProjectCommunityApplication;
import opus.gwt.management.console.client.overlays.ProjectData;
import opus.gwt.management.console.client.overlays.ProjectFieldData;
import opus.gwt.management.console.client.overlays.ProjectManualApplication;
import opus.gwt.management.console.client.overlays.VersionData;
import opus.gwt.management.console.client.resources.ProjectBuilderCss.ProjectBuilderStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DisclosurePanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AddAppsBuildProject extends Composite {

	private static AddAppsBuildProjectUiBinder uiBinder = GWT
	.create(AddAppsBuildProjectUiBinder.class);

	interface AddAppsBuildProjectUiBinder extends
		UiBinder<Widget, AddAppsBuildProject> {
	}
	
	private final String tokenURL = "/project/configuration/token/?callback=";
	private final String appFieldListURL = "/model/fields/application/?a";
	private final String searchURL = "/search/application/json/?a";
	private final String getVersionsURL = "/name/versions/?a&callback=";
	
	private String JSON_URL;
	private Label errorMsgLabel = new Label();
	private String selectedApp = "";
	private ArrayList<String> paths = new ArrayList<String>();
	private ArrayList<String> apps = new ArrayList<String>();
	private ArrayList<String> types = new ArrayList<String>();
	private ServerCommunicator jsonCom;

	private ApplicationPopup appInfoDialog = new ApplicationPopup();
	private AddOtherApplication addOtherDialog = new AddOtherApplication(this);
	private AddProjectFromURL addProject = new AddProjectFromURL(this);
	
	private ProjectDeployer appDeployer;
	private JSVariableHandler JSVarHandler;
	
	@UiField Button searchButton;
	@UiField TextBox searchBox;
	@UiField ListBox fieldList;
	@UiField FlexTable appListFlexTable;
	@UiField FlexTable deployListFlexTable;
	@UiField Button nextButton;
	//@UiField PopupPanel fieldPopup;
	@UiField ScrollPanel infoScrollPanel;
	@UiField Button addOtherButton;
	@UiField Button addExistingProjectButton;
	@UiField ProjectBuilderStyle style;

	
	public AddAppsBuildProject(ProjectDeployer appDeployer, ServerCommunicator jsonCom) {
		JSVarHandler = new JSVariableHandler();
		JSON_URL = URL.encode(JSVarHandler.getRepoBaseURL() + searchURL);
		initWidget(uiBinder.createAndBindUi(this));
		this.jsonCom = jsonCom;
		this.refreshAppListFlexTable(URL.encode(JSVarHandler.getRepoBaseURL() + searchURL));
		this.populateFieldList(URL.encode(JSVarHandler.getRepoBaseURL() + appFieldListURL));
		this.appDeployer = appDeployer;	
		String token = JSVarHandler.getProjectToken();
		if (token != null) {
			this.addProject(URL.encode(JSVarHandler.getRepoBaseURL() + tokenURL.replaceAll("token", token)));
		}
	}

	public Object asObject(AddAppsBuildProject a){
		return a;
	}
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		//appDeployer.handleProjectOptionsLabel();
	}

	@UiHandler("addOtherButton")
	void handleAddOtherButton(ClickEvent event){
		addOtherDialog.show();
	}
	/**
	   * Generate random stock prices.
	   */
	  private void refreshAppListFlexTable(String url) {
	    // Clear table
		appListFlexTable.removeAllRows();
		  
	    // Append the name of the callback function to the JSON URL.
	    url = URL.encode(url) + "&callback=";

	    // Send request to server by replacing RequestBuilder code with a call to a JSNI method.
	    jsonCom.getJson(url, jsonCom, "updateTable", this);
	  }
	  
	  /**
	   * Generate list of fields to search on
	   * @param e
	   */
	  private void populateFieldList(String url) {
		  url = URL.encode(url) + "&callback=";
		  jsonCom.getJson(url, jsonCom, "updateFieldList", this);
	  }
	  
	  
	  @UiHandler("searchButton")
	  void handleSearchClick(ClickEvent e) {
		  this.search();
	  }
	  
	  @UiHandler("searchBox")
	  void handleKeyPress(KeyPressEvent event) {
		  if (event.getCharCode() == KeyCodes.KEY_ENTER) {
	          this.search();
	      }
	  }
	  
	  @UiHandler("addExistingProjectButton")
	  void handleURLClick(ClickEvent e) {
		  addProject.show();
	  }

	  private void search() {
		  String query = searchBox.getText().trim();
		  if (!query.isEmpty()) {
			  String url = URL.encode(JSVarHandler.getRepoBaseURL() + searchURL + "&field=" + fieldList.getValue(fieldList.getSelectedIndex()) + "&query=" + query);
			  this.refreshAppListFlexTable(url);
		  } else {
			  this.refreshAppListFlexTable(URL.encode(JSVarHandler.getRepoBaseURL() + searchURL));
		  }
		  searchBox.setText("");
	  }

	  /**
	   * Update the Price and Change fields all the rows in the stock table.
	   *
	   * @param prices Stock data for all rows.
	   */
	  public void updateTable(JsArray<AppData> prices) {
	    for (int i = 0; i < prices.length(); i++) {
	      updateTable(prices.get(i), jsonCom);
	    }

	    // Clear any errors.
	    errorMsgLabel.setVisible(false);
	  }
	  
	  public void updateTable(AppData app, final ServerCommunicator handler) {
		  final AddAppsBuildProject p = this;
		  //Add the app to the table.
		  int row = appListFlexTable.getRowCount();
		  final String description = app.getDescription();
		  final String name = app.getName();
		  String shortDescription;
		  if (description.length() > 100) {
			  shortDescription = app.getDescription().substring(0, 99) + " ...";
		  } else {
			  shortDescription = app.getDescription();
		  }
			  //		  appListFlexTable.setText(row, 0, appinfo);
		  
		  HTMLPanel appInfoPanel = new HTMLPanel(("<b>" + name + "</b> -" + shortDescription));
		  //appInfoPanel.addStyleName("style.cellHTMLPanel");
		  Button addAppButton = new Button();
		  addAppButton.addStyleName("addAppButton");
		  addAppButton.setText("Add to List");
		  final String url = URL.encode(JSVarHandler.getRepoBaseURL() + getVersionsURL.replaceAll("name", name));
		  addAppButton.addClickHandler(new ClickHandler() {
		      public void onClick(ClickEvent event) {
		    	  selectedApp = name;
		    	  appInfoDialog.versionsFlexTable.clear(true);
		    	  appInfoDialog.versionsFlexTable.removeAllRows();
		    	  int row = appInfoDialog.versionsFlexTable.getRowCount();
		    	  //Window.alert(String.valueOf(row));
		    	  appInfoDialog.versionsFlexTable.setHTML(row, 0, "<div><b>" + name + "</b> -" + description + "</div>");
		    	  //appInfoDialog.versionsFlexTable.setText(row, 0, "hello");
		    	  jsonCom.getJson(url, handler, "handleVersions", p);
		    	  //Window.alert(url);
		    	  
	//	    	  appInfoDialog.versionsFlexTable.setWidget(row, 0, new HTMLPanel("<div><b>" + name + "</b> -" + description + "</div>"));
		        }
		      });
		  appListFlexTable.setWidget(row, 0, appInfoPanel);
		  appListFlexTable.setWidget(row, 1, addAppButton);
		  appListFlexTable.getCellFormatter().addStyleName(row, 0, style.appCell());
		  appListFlexTable.getCellFormatter().addStyleName(row, 1, style.appCell());
		  //appInfoPanel.addStyleName("appCell");
	  }
	  
	  
	  
	  public void updateFieldList(ModelProperties properties) {
		  String fields = properties.getFields().toString();
		  //Window.alert(fields);
		  String[] fieldArray  = fields.split(",");
		  
		  for (int i = 0; i < fieldArray.length; i++) {
			  fieldList.addItem(fieldArray[i],fieldArray[i]);
		  }

	  }
	  
	  public void handleVersions(JsArray<VersionData> versions){
		  final AddAppsBuildProject appBuilder = this;
		  for (int i = 0; i < versions.length(); i++){
			  final String appString = selectedApp + " " + versions.get(i).getVersion();
			  final String appPath = versions.get(i).getPath();
			  DisclosurePanel versionPanel = new DisclosurePanel("Version " + versions.get(i).getVersion());
			  versionPanel.setAnimationEnabled(true);
			  JsArray<DependencyData> dependencies = versions.get(i).getDependencies();
			  String html = "";
			  for (int j = 0; j < dependencies.length(); j++) {
				  html += dependencies.get(j).getName() + " " + dependencies.get(j).getVersion() + "<br>";
			  }
			  versionPanel.setContent(new HTML(html));	
			  int row = appInfoDialog.versionsFlexTable.getRowCount();
			  appInfoDialog.versionsFlexTable.setWidget(row, 0, versionPanel);
			  Button addButton = new Button();
			  addButton.setText("Add");
			  addButton.addClickHandler(new ClickHandler() {
		      public void onClick(ClickEvent event) {
		    	  appBuilder.addApp(appString, appPath, "git");
		      	}
		      });
			  appInfoDialog.versionsFlexTable.setWidget(row, 1, addButton);
		  }
		  appInfoDialog.show();
	  }
	  
	  public ArrayList<String> getAppPaths(){
		  return paths;
	  }
	  
	  public ArrayList<String> getAppTypes(){
		  return types;
	  }
	  
	  public void addApp(String name, String path, String type){
		  final String nameString = name;
		  final String pathString = path;
		  final String typeString = type;
    	  if (!apps.contains(nameString)){
    		  apps.add(nameString);
    		  paths.add(pathString);
    		  types.add(typeString);
    		  final int row = deployListFlexTable.getRowCount();
	    	  deployListFlexTable.setHTML(row, 0, "<div><b>" + nameString+ "</b></div>");
	    	  Button removeButton = new Button();
	    	  removeButton.setText("Remove");
	    	  removeButton.addClickHandler(new ClickHandler() {
	    		 public void onClick(ClickEvent event) {
	    			 if (apps.contains(nameString)){
	    				 int removedIndex = apps.indexOf(nameString);
	    				 apps.remove(nameString);
	    				 paths.remove(pathString);
	    				 paths.remove(typeString);
	    				 deployListFlexTable.removeRow(removedIndex);
	    			 }
	    		 }
	    	  });
	    	  deployListFlexTable.setWidget(row, 1, removeButton);
	    	  selectedApp = "";
	    	  appInfoDialog.hide();
    	  }
	  }
	  
	  public void addProject(String url){
		  jsonCom.getJson(url, jsonCom, "importAppList", this);
	  }
	  
	  public void importAppList(JsArray<ProjectData> projectDataArray) {
		  ProjectData projectData = projectDataArray.get(0);

		  ProjectFieldData fields = projectData.getFields();
		  JsArray<ProjectManualApplication>manualApps = fields.getAsArrayOfManualApps();
		  JsArray<ProjectCommunityApplication>communityApps = fields.getAsArrayOfCommunityApps();
		  apps.clear();
		  paths.clear();
		  deployListFlexTable.removeAllRows();
		  for (int i=0; i < communityApps.length(); i++){
			  this.addApp(communityApps.get(i).getName(), communityApps.get(i).getPath(), communityApps.get(i).getType());
		  }
		  
		  for (int i=0; i < manualApps.length(); i++){
			  this.addApp(manualApps.get(i).getName(), manualApps.get(i).getPath(), manualApps.get(i).getType());
		  }
	  }
	  
	  public ArrayList<String> getApps(){
		  return apps;
	  }
	  public FlexTable getDeployListFlexTable(){
		  return deployListFlexTable;
	  }
	  /**
	   * Cast JavaScriptObject as JsArray of StockData.
	   */
	  public final native JsArray<AppData> asArrayOfAppData(JavaScriptObject jso) /*-{
	    return jso;
	  }-*/;
	  
	  /**
	   * Cast JavaScriptObject as ModelProperties.
	   */
	  public final native ModelProperties asModelProperties(JavaScriptObject jso) /*-{
	    return jso;
	  }-*/;
	  
	  public final native JsArray<VersionData> asArrayOfVersionData(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;
	  
	  public final native JsArray<ProjectData> asArrayOfProjectData(JavaScriptObject jso) /*-{
 		return jso;
	  }-*/;
	  public final native JsArray<ProjectFieldData> asArrayOfProjectFieldData(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;
	  
	  public final native JsArray<ProjectManualApplication> asArrayOfProjectManualApplications(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;	
	  
	  public final native JsArray<ProjectCommunityApplication> asArrayOfProjectCommunityApplications(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;
}
