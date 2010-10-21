package opus.gwt.management.console.client.dashboard;

import java.util.ArrayList;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ManagementConsoleController;
import opus.gwt.management.console.client.deployer.ErrorPanel;
import opus.gwt.management.console.client.event.AsyncRequestEvent;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.overlays.ProjectSettingsData;
import opus.gwt.management.console.client.resources.ProjectManagerCss.ProjectManagerStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class ProjectSettingsPanel extends Composite {

	interface ProjectSettingsUiBinder extends UiBinder<Widget, ProjectSettingsPanel> {}
	private static ProjectSettingsUiBinder uiBinder = GWT.create(ProjectSettingsUiBinder.class);
	
	private final String optionsUrl = "/deployments/projectName/confapps/";
	
	private String projectName;
	private JSVariableHandler jsVarHandler;
	private boolean active;
	private ManagementConsoleController managementCon;
	private ProjectManagerController projectManagerController;
	private boolean hasSettings;
	private ArrayList<String> textboxes;
	
	@UiField FlexTable formContainer;
	@UiField FormPanel optionsForm;
	@UiField Button SaveButton;
	@UiField Button ActivateButton;
	@UiField Label WarningLabel;
	@UiField ProjectManagerStyle style;


	public ProjectSettingsPanel(EventBus eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.projectName = "";
		this.jsVarHandler = new JSVariableHandler();
		this.projectManagerController = projectManagerController;
		this.optionsForm = new FormPanel();
		this.textboxes = new ArrayList<String>();
		setupOptionsForm();
		registerHandlers();
	}
	
	private void registerHandlers(){
		
	}
	
	public void setupOptionsForm(){
		optionsForm.setAction((jsVarHandler.getDeployerBaseURL() + optionsUrl.replaceAll("projectName", this.projectName))); 
		optionsForm.setMethod(FormPanel.METHOD_POST);
		optionsForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
			public void onSubmitComplete(SubmitCompleteEvent event) {
		        //managementCon.onDeployNewProject(projectName);
		        //RootPanel.detachNow(optionsForm);
		    }
			});
	}
	
	public void importProjectSettings(ProjectSettingsData settings, String[] apps){
		int row = 0;
		for (int i=0; i<apps.length; i++){
			
			//Create header for app
			Label appName = new Label();
			appName.setText(apps[i]);
			appName.addStyleName("SettingsAppName");
			formContainer.setWidget(row++, 0, appName);
			//Get list of settings for app
			
			JsArray<JavaScriptObject> appsettings = settings.getAppSettings(apps[i]);
			for(int j=0; j<appsettings.length(); j++){
				//Window.alert(String.valueOf(j));
				JsArray<JavaScriptObject> p = settings.getSettingsArray(appsettings.get(j));
				String[] parts = p.join(";;").split(";;\\s*");
				if (parts[2].equals("string")){
					TextBox setting = new TextBox();
					setting.setName(apps[i]+"-"+parts[0]);
					setting.getElement().setId(apps[i]+parts[0]);
					//Check default value
					if (parts.length > 3){
						//Window.alert("gotcha");
						//setting.setValue(parts[3]);
						setting.setText(parts[3]);
					}
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					settingLabel.addStyleName("SettingLabel");
					setting.setStyleName("SettingInput");
					formContainer.setWidget(row, 0,settingLabel);
					formContainer.setWidget(row++, 1,setting);
					textboxes.add(setting.getElement().getId());
					//textboxes[textboxes.length] = setting;
					//textboxes.add(setting);
				} else if(parts[2].equals("int")){
					TextBox setting = new TextBox();
					//Check default value
					if (parts.length > 3){
						//setting.setValue(parts[3]);
						setting.setText(parts[3]);
					}
					setting.setName(apps[i]+"-"+parts[0]);
					setting.getElement().setId(apps[i]+parts[0]);
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					settingLabel.addStyleName("SettingLabel");
					setting.setStyleName("SettingInput");
					formContainer.setWidget(row, 0,settingLabel);
					formContainer.setWidget(row++, 1,setting);
					textboxes.add(setting.getElement().getId());
					//textboxes.add(setting);
				} else if(parts[2].equals("choice")){
					ListBox setting = new ListBox();
					setting.setName(apps[i]+"-"+parts[0]);
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					setting.getElement().setInnerHTML(parts[3]);
					settingLabel.addStyleName("SettingLabel");
					setting.setStyleName("SettingInput");
					formContainer.setWidget(row, 0,settingLabel);
					formContainer.setWidget(row++, 1,setting);
				} else if(parts[2].equals("bool")) {
					CheckBox setting = new CheckBox();
					if (parts.length > 3){
						//setting.setValue(parts[3]);
						setting.setValue(Boolean.valueOf(parts[3]));
					}
					setting.setName(apps[i]+"-"+parts[0]);
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					settingLabel.addStyleName("SettingLabel");
					setting.setStyleName("SettingInput");
					formContainer.setWidget(row, 0,settingLabel);
					formContainer.setWidget(row++, 1,setting);
				}
			}
			formContainer.setHTML(row, 0, "<hr width=\"80%\">");
			formContainer.getFlexCellFormatter().setColSpan(row++, 0, 2);

		}
		this.hasSettings = true;
		//setActive(projectManagerController.getDashboard().isActive());
	}
	
	public void setHasSettings(boolean state) {
		this.hasSettings = state;
	}
	
	//ProjectManagerController.displayOptions() calls this function  
	public void setActive(boolean active){
		this.active = active;
		if(!active){
			if(hasSettings){
				WarningLabel.setText("You must fill out all the settings and click \"Save and Activate\" button in order start using project.");
			} else {
				WarningLabel.setText("This project is not active.  Press the Activate button to activate it.");
				ActivateButton.setText("Activate");
				SaveButton.setVisible(false);
			}
			WarningLabel.setStyleName(style.WarningLabel());
		} else {
			WarningLabel.setText("");
			ActivateButton.setText("Deactivate");
			SaveButton.setVisible(true);
			//Button.setText("Submit");
		}
	}
	
	private boolean validateForm(){
		for(String t : textboxes){
			//Window.alert(getValue(t));
			/*if (DOM.getElementById(t).getInnerText().length() == 0) {
				Window.alert("All settings are required.");
				return false;
			}*/
		}
		return true;
	}
	
	public final native String getValue(String id) /*-{ 
		alert("hello");
		return document.getElementById(id).value; }-*/;
	
	@UiHandler("SaveButton")
	void handleSaveButton(ClickEvent event){
		if( validateForm() ){

			//formContainer.setWidget(formContainer.getRowCount(), 0, new Hidden("csrfmiddlewaretoken", jsVarHandler.getCSRFTokenURL()));
			optionsForm.add(formContainer);
			//optionsForm.submit();
			
			saveSettings();
		}
	}
	@UiHandler("ActivateButton")
	void handleActivateButton(ClickEvent event){
		if( validateForm() ){
			formContainer.setWidget(formContainer.getRowCount(), 0, new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
			TextBox activeField = new TextBox();
			activeField.setVisible(false);
			activeField.setName("active");
			if(this.active) {
				activeField.setText("false");
				//TextBox activate = new TextBox();
				//activate.setName("activate");
				//formContainer.setWidget(formContainer.getRowCount(), 1, activate);
			} else {
				activeField.setText("true");
			}
			formContainer.setWidget(formContainer.getRowCount(), 1, activeField);
			optionsForm.add(formContainer);
	
			//RootPanel.get().add(optionsForm);
			optionsForm.submit();
		}
	}
	
	private void saveSettings(){
	    RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, optionsUrl.replaceAll("projectName", this.projectName));
	    builder.setHeader("Content-type", "application/x-www-form-urlencoded");
		
	    StringBuffer formBuilder = new StringBuffer();
	    
	    formBuilder.append("csrfmiddlewaretoken=");
		formBuilder.append( URL.encodeQueryString(jsVarHandler.getCSRFTokenURL()));
		
	    try {
		      Request request = builder.sendRequest(formBuilder.toString(), new RequestCallback() {
		        public void onError(Request request, Throwable exception) {
		        	Window.alert("ERORR SENDING FORM WITH REQUEST BUILDER");
		        }

		        public void onResponseReceived(Request request, Response response) {
			    	if( response.getText().contains("") ){
			    	
			    	} else {
			    	
			    	}
		        }});
		    } catch (RequestException e) {
		    	
		    }
	}
}
