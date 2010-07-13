package opus.community.gwt.management.console.client.deployer;

import java.util.ArrayList;

import opus.community.gwt.management.console.client.ServerCommunicator;

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
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AddAppsBuildProject extends Composite {

	private static final String JSON_URL = "https://opus-dev.cnl.ncsu.edu:9004/opus_community/search/application/json/?a";
	private Label errorMsgLabel = new Label();
	private String selectedApp = "";
	private ArrayList<String> paths = new ArrayList<String>();
	private ArrayList<String> apps = new ArrayList<String>();
	private ServerCommunicator jsonCom;

	private static AddAppsBuildProjectUiBinder uiBinder = GWT
			.create(AddAppsBuildProjectUiBinder.class);

	private ApplicationDetailDialog appInfoDialog = new ApplicationDetailDialog();
	private AddOtherApplication addOtherDialog = new AddOtherApplication(this);
	
	interface AddAppsBuildProjectUiBinder extends
			UiBinder<Widget, AddAppsBuildProject> {
	}

	private applicationDeployer appDeployer;
	
	@UiField Button searchButton;
	@UiField TextBox searchBox;
	@UiField ListBox fieldList;
	@UiField FlexTable appListFlexTable;
	@UiField FlexTable deployListFlexTable;
	@UiField Button nextButton;
	//@UiField PopupPanel fieldPopup;
	@UiField ScrollPanel infoScrollPanel;
	@UiField Button addOtherButton;

	public AddAppsBuildProject(applicationDeployer appDeployer, FormPanel form, ServerCommunicator jsonCom) {
		initWidget(uiBinder.createAndBindUi(this));
		this.jsonCom = jsonCom;
		this.refreshAppListFlexTable(JSON_URL);
		this.populateFieldList("https://opus-dev.cnl.ncsu.edu:9004/opus_community/model/fields/application/?a");
		this.appDeployer = appDeployer;	
	}

	public Object asObject(AddAppsBuildProject a){
		return a;
	}
	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		appDeployer.handleProjectOptionsLabel();
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
	    jsonCom.getJson(url, jsonCom,1,(Object)this);
	  }
	  
	  /**
	   * Generate list of fields to search on
	   * @param e
	   */
	  private void populateFieldList(String url) {
		  url = URL.encode(url) + "&callback=";
		  jsonCom.getJson(url, jsonCom, 2, (Object)this);
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
	  
	  /*@UiHandler("nextButton")
	  void handleSubmitClick(ClickEvent eve) {
		  ArrayList<String> postData = new ArrayList<String>();
		  for(int i=0; i < paths.size(); i++) {
			  postData.add("{\"type\":\"git\",\"path\":\""+paths.get(i)+"\"}");
		  }
		  this.doPost("https://opus-dev.cnl.ncsu.edu:9007/deployments/testname/", "json="+postData.toString());
	  }*/

	  
	  private void search() {
		  String query = searchBox.getText().trim();
		  if (!query.isEmpty()) {
			  String url = JSON_URL+"&field=" + fieldList.getValue(fieldList.getSelectedIndex()) + "&query="+query;
			  this.refreshAppListFlexTable(url);
		  } else {
			  this.refreshAppListFlexTable(JSON_URL);
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
		  appInfoPanel.addStyleName("style.cellHTMLPanel");
		  Button addAppButton = new Button();
		  addAppButton.addStyleName("addAppButton");
		  addAppButton.setText("Add to List");
		  final String url = URL.encode("https://opus-dev.cnl.ncsu.edu:9004/opus_community/" + name + "/versions/?a") + "&callback=";
		  addAppButton.addClickHandler(new ClickHandler() {
		      public void onClick(ClickEvent event) {
		    	  selectedApp = name;
		    	  appInfoDialog.versionsFlexTable.clear(true);
		    	  appInfoDialog.versionsFlexTable.removeAllRows();
		    	  int row = appInfoDialog.versionsFlexTable.getRowCount();
		    	  //Window.alert(String.valueOf(row));
		    	  appInfoDialog.versionsFlexTable.setHTML(row, 0, "<div><b>" + name + "</b> -" + description + "</div>");
		    	  //appInfoDialog.versionsFlexTable.setText(row, 0, "hello");
		    	  jsonCom.getJson(url,handler,3,(Object)p);
		    	  
		    	  
	//	    	  appInfoDialog.versionsFlexTable.setWidget(row, 0, new HTMLPanel("<div><b>" + name + "</b> -" + description + "</div>"));
		        }
		      });
		  appListFlexTable.setWidget(row, 0, appInfoPanel);
		  appListFlexTable.setWidget(row, 1, addAppButton);
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
			  final String appString = selectedApp + versions.get(i).getVersion();
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
		    	  appBuilder.addApp(appString, appPath);
		      	}
		      });
			  appInfoDialog.versionsFlexTable.setWidget(row, 1, addButton);
		  }
		  appInfoDialog.show();
	  }
	  
	  public ArrayList<String> getAppPaths(){
		  return paths;
	  }
	  
	  public void addApp(String name, String path){
		  final String nameString = name;
		  final String pathString = path;
    	  if (!apps.contains(nameString)){
    		  apps.add(nameString);
    		  paths.add(pathString);
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
	    				 deployListFlexTable.removeRow(removedIndex);
	    			 }
	    		 }
	    	  });
	    	  deployListFlexTable.setWidget(row, 1, removeButton);
	    	  selectedApp = "";
	    	  appInfoDialog.hide();
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


	
}
