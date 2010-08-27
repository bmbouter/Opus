package opus.gwt.management.console.client.dashboard;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ManagementConsole;
import opus.gwt.management.console.client.ServerCommunicator;
import opus.gwt.management.console.client.resources.ProjectDashboardCss.ProjectDashboardStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
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
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class ProjectSettings extends Composite {

	private ServerCommunicator communicator;
	private final String optionsUrl = "deployments/projectName/confapps";
	private String projectName;
	private JSVariableHandler JSVarHandler;
	private boolean active;
	private ManagementConsole managementCon;
	private ProjectDashboard projectDashboard;
	private boolean hasSettings;
	
	private static ProjectSettingsUiBinder uiBinder = GWT
			.create(ProjectSettingsUiBinder.class);
	
	@UiField FlexTable formContainer;
	@UiField FormPanel optionsForm;
	@UiField Button SaveButton;
	@UiField Button ActivateButton;
	@UiField Label WarningLabel;
	@UiField ProjectDashboardStyle style;
	
	interface ProjectSettingsUiBinder extends UiBinder<Widget, ProjectSettings> {
	}

	public ProjectSettings(String projectName, ManagementConsole manCon, ProjectDashboard projectDashboard) {
		initWidget(uiBinder.createAndBindUi(this));
		this.projectName = projectName;
		this.JSVarHandler = new JSVariableHandler();
		this.managementCon = manCon;
		this.projectDashboard = projectDashboard;
		this.optionsForm = new FormPanel();
		setupOptionsForm();
	}
	
	public void setupOptionsForm(){
		optionsForm.setAction((JSVarHandler.getDeployerBaseURL() + optionsUrl.replaceAll("projectName", this.projectName))); 
		optionsForm.setMethod(FormPanel.METHOD_POST);
		optionsForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
			public void onSubmitComplete(SubmitCompleteEvent event) {
		        managementCon.onDeployNewProject(projectName);
		        RootPanel.detachNow(optionsForm);
		    }
			});
	}
	
	//Dashboard.handleProjectInformation() calls this method to import settings
	public void importProjectSettings(ProjectSettingsData settings, String[] apps){
		//Window.alert("importing settings");
		for (int i=0; i<apps.length; i++){
			int row = 0;
			//Create header for app
			Label appName = new Label();
			appName.setText(apps[i]);
			appName.addStyleName("SettingsAppName");
			formContainer.setWidget(row++, 0, appName);
			//Get list of settings for app
			
			JsArray<JavaScriptObject> appsettings = settings.getAppSettings(apps[i]);
			for(int j=0; j<appsettings.length(); j++){
				JsArray<JavaScriptObject> p = settings.getSettingsArray(appsettings.get(j));
				String[] parts = p.join(";;;").split(";;;\\s*");
				if (parts[2].equals("string")){
					TextBox setting = new TextBox();
					setting.setName(apps[i]+"-"+parts[0]);
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

				} else if(parts[2].equals("int")){
					TextBox setting = new TextBox();
					//Check default value
					if (parts.length > 3){
						//setting.setValue(parts[3]);
						setting.setText(parts[3]);
					}
					setting.setName(apps[i]+"-"+parts[0]);
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					settingLabel.addStyleName("SettingLabel");
					setting.setStyleName("SettingInput");
					formContainer.setWidget(row, 0,settingLabel);
					formContainer.setWidget(row++, 1,setting);
					
				} else if(parts[2].equals("choice")){
					ListBox setting = new ListBox();
					setting.setName(apps[i]+"-"+parts[0]);
					Label settingLabel = new Label();
					settingLabel.setText(parts[1]);
					for(int k=3; k<parts.length; k++){
						setting.addItem(parts[++k], parts[k-1]);
						
						if(parts[++k].equals("true")){
							setting.setItemSelected(setting.getItemCount()-1, true);
						}
					}
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
			formContainer.setHTML(row, 0, "<hr width=\"90%\">");
			formContainer.getFlexCellFormatter().setColSpan(row++, 0, 2);

		}
		this.hasSettings = true;
		//setActive(projectDashboard.getDashboard().isActive());
	}
	
	public void setHasSettings(boolean state) {
		this.hasSettings = state;
	}
	
	//ProjectDashboard.displayOptions() calls this function  
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
			SaveButton.setVisible(false);
			//Button.setText("Submit");
		}
	}
	
	@UiHandler("SaveButton")
	void handleSaveButton(ClickEvent event){
		//SaveButton.getElement().setAttribute("name", "Save");
		formContainer.setWidget(formContainer.getRowCount(), 0, new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
		optionsForm.add(formContainer);
		RootPanel.get().add(optionsForm);
		optionsForm.submit();
	}
	@UiHandler("ActivateButton")
	void handleActivateButton(ClickEvent event){
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

		RootPanel.get().add(optionsForm);
		optionsForm.submit();
	}
	public final native ProjectSettingsData asProjectSettings(JavaScriptObject jso) /*-{
		alert("ssss");
		return jso;
	}-*/;

}
