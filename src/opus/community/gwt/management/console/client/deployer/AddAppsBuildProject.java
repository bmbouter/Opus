package opus.community.gwt.management.console.client.deployer;

import java.util.ArrayList;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DisclosurePanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class AddAppsBuildProject extends Composite {

	private static final String JSON_URL = "https://opus-dev.cnl.ncsu.edu:9004/opus_community/search/application/json/?a";
	private Label errorMsgLabel = new Label();
	private int jsonRequestId = 0;
	private String selectedApp = "";
	private String selectedAppPath = "";
	private ArrayList<String> paths = new ArrayList<String>();
	private ArrayList<String> apps = new ArrayList<String>();

	private static AddAppsBuildProjectUiBinder uiBinder = GWT
			.create(AddAppsBuildProjectUiBinder.class);

	private ApplicationDetailDialog appInfoDialog = new ApplicationDetailDialog();

	
	interface AddAppsBuildProjectUiBinder extends
			UiBinder<Widget, AddAppsBuildProject> {
	}
	private FormPanel deployerForm;
	private applicationDeployer appDeployer;
	
	@UiField Button searchButton;
	@UiField TextBox searchBox;
	@UiField ListBox fieldList;
	@UiField FlexTable appListFlexTable;
	@UiField FlexTable deployListFlexTable;
	@UiField Button nextButton;
	//@UiField PopupPanel fieldPopup;
	@UiField ScrollPanel infoScrollPanel;


	public AddAppsBuildProject(applicationDeployer appDeployer, FormPanel form) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = form;
		this.refreshAppListFlexTable(JSON_URL);
		this.populateFieldList("https://opus-dev.cnl.ncsu.edu:9004/opus_community/model/fields/application/?a");
		this.appDeployer = appDeployer;
		
		

	}

	@UiHandler("nextButton")
	void handleNextButton(ClickEvent event){
		appDeployer.handleProjectOptionsLabel();
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
	    getJson(jsonRequestId++, url, this,1);
	  }
	  
	  /**
	   * Generate list of fields to search on
	   * @param e
	   */
	  private void populateFieldList(String url) {
		  
		  url = URL.encode(url) + "&callback=";
		  getJson(jsonRequestId++, url, this, 2);
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
	   * If can't get JSON, display error message.
	   * @param error
	   */
	  private void displayError(String error) {
	    errorMsgLabel.setText("Error: " + error);
	    errorMsgLabel.setVisible(true);
	  }
	  
	  /**
	   * Make call to remote server.
	   */
	  public native static void getJson(int requestId, String url,
	      AddAppsBuildProject handler, int queryType) /*-{
	   
	   var callback = "callback" + requestId;
	   
	   // [1] Create a script element.
	   var script = document.createElement("script");
	   script.setAttribute("src", url+callback);
	   script.setAttribute("type", "text/javascript");

	   // [2] Define the callback function on the window object.
	   window[callback] = function(jsonObj) {
	   // [3]
	     handler.@opus.community.gwt.management.console.client.deployer.AddAppsBuildProject::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;I)(jsonObj, queryType);
	     window[callback + "done"] = true;
	   }

	   // [4] JSON download has 1-second timeout.
	   setTimeout(function() {
	     if (!window[callback + "done"]) {
	       handler.@opus.community.gwt.management.console.client.deployer.AddAppsBuildProject::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;I)(null);
	     }

	     // [5] Cleanup. Remove script and callback elements.
	     document.body.removeChild(script);
	     delete window[callback];
	     delete window[callback + "done"];
	   }, 1000);

	   // [6] Attach the script element to the document body.
	   document.body.appendChild(script);
	  }-*/;
	  
	  /**
	   * Handle the response to the request for stock data from a remote server.
	   */
	  public void handleJsonResponse(JavaScriptObject jso, int queryType) {
	    if (jso == null) {
	      displayError("Couldn't retrieve JSON");
	      return;
	    }
	    //Window.alert(Integer.toString(queryType));
	    if (queryType == 1) {
	    	updateTable(asArrayOfAppData (jso));
	    } else if (queryType == 2) {
	    	updateFieldList(asModelProperties(jso));
	    } else if (queryType == 3) {
	    	handleVersions(asArrayOfVersionData(jso));
	    }
	  }
	
	  /**
	   * Update the Price and Change fields all the rows in the stock table.
	   *
	   * @param prices Stock data for all rows.
	   */
	  private void updateTable(JsArray<AppData> prices) {
	    for (int i = 0; i < prices.length(); i++) {
	      updateTable(prices.get(i), this);
	    }

	    // Clear any errors.
	    errorMsgLabel.setVisible(false);
	  }
	  
	  private void updateTable(AppData app, final AddAppsBuildProject handler) {
		// Add the app to the table.
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
		    	  int row = appInfoDialog.versionsFlexTable.getRowCount();
		    	  appInfoDialog.versionsFlexTable.removeAllRows();
		    	  appInfoDialog.versionsFlexTable.setHTML(row, 0, "<div><b>" + name + "</b> -" + description + "</div>");
		    	  //appInfoDialog.versionsFlexTable.setText(row, 0, "hello");
		    	  AddAppsBuildProject.getJson(jsonRequestId++,url,handler,3);
		    	  
		    	  
	//	    	  appInfoDialog.versionsFlexTable.setWidget(row, 0, new HTMLPanel("<div><b>" + name + "</b> -" + description + "</div>"));
		        }
		      });
		  appListFlexTable.setWidget(row, 0, appInfoPanel);
		  appListFlexTable.setWidget(row, 1, addAppButton);
	  }
	  
	  
	  
	  private void updateFieldList(ModelProperties properties) {
		  String fields = properties.getFields().toString();
		  //Window.alert(fields);
		  String[] fieldArray  = fields.split(",");
		  
		  for (int i = 0; i < fieldArray.length; i++) {
			  fieldList.addItem(fieldArray[i],fieldArray[i]);
		  }

	  }
	  
	  private void handleVersions(JsArray<VersionData> versions){
		  
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
		    	  if (!apps.contains(appString)){
		    		  apps.add(appString);
		    		  paths.add(appPath);
		    		  final int row = deployListFlexTable.getRowCount();
			    	  deployListFlexTable.setHTML(row, 0, "<div><b>" + selectedApp+ "</b></div>");
			    	  Button removeButton = new Button();
			    	  removeButton.setText("Remove");
			    	  removeButton.addClickHandler(new ClickHandler() {
			    		 public void onClick(ClickEvent event) {
			    			 if (apps.contains(appString)){
			    				 int removedIndex = apps.indexOf(appString);
			    				 apps.remove(appString);
			    				 paths.remove(appPath);
			    				 deployListFlexTable.removeRow(removedIndex);
			    			 }
			    		 }
			    	  });
			    	  deployListFlexTable.setWidget(row, 1, removeButton);
			    	  selectedApp = "";
			    	  appInfoDialog.hide();
		    	  }
		        }
		      });
			  appInfoDialog.versionsFlexTable.setWidget(row, 1, addButton);
		  }
		  appInfoDialog.show();
	  }
	  
	  public ArrayList<String> getAppPaths(){
		  return paths;
	  }
	  
	  public void doPost(String url, String postData) {
		    RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, url);
		    Window.alert(postData);
		    try {
		      Request response = builder.sendRequest(postData, new RequestCallback() {

		        public void onError(Request request, Throwable exception) {
		          Window.alert(exception.getLocalizedMessage());
		        }

		        public void onResponseReceived(Request request, Response response) {
		        	Window.alert(response.toString());
		        	Window.alert(response.getStatusText());
		        }
		      });
		      
		    } catch (RequestException e) {
		      Window.alert("Failed to send the request: " + e.getMessage());
		    }   
	  }
	  
	  /**
	   * Cast JavaScriptObject as JsArray of StockData.
	   */
	  private final native JsArray<AppData> asArrayOfAppData(JavaScriptObject jso) /*-{
	    return jso;
	  }-*/;
	  
	  /**
	   * Cast JavaScriptObject as ModelProperties.
	   */
	  private final native ModelProperties asModelProperties(JavaScriptObject jso) /*-{
	    return jso;
	  }-*/;
	  
	  private final native JsArray<VersionData> asArrayOfVersionData(JavaScriptObject jso) /*-{
	  	return jso;
	  }-*/;


	
}
