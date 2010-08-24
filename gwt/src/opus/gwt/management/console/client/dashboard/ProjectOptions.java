package opus.gwt.management.console.client.dashboard;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.ManagementConsole;
import opus.gwt.management.console.client.ServerCommunicator;
import opus.gwt.management.console.client.deployer.ProjectData;
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
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class ProjectOptions extends Composite {

	private ServerCommunicator communicator;
	private final String optionsUrl = "deployments/projectName/confapps";
	private String projectName;
	private JSVariableHandler JSVarHandler;
	private boolean active;
	private ManagementConsole managementCon;
	private ProjectDashboard projectDashboard;
	
	private static ProjectOptionsUiBinder uiBinder = GWT
			.create(ProjectOptionsUiBinder.class);
	
	@UiField FlexTable formContainer;
	@UiField FormPanel optionsForm;
	@UiField Button SaveButton;
	@UiField Button ActivateButton;
	@UiField Label WarningLabel;
	@UiField ProjectDashboardStyle style;
	
	interface ProjectOptionsUiBinder extends UiBinder<Widget, ProjectOptions> {
	}

	public ProjectOptions(String projectName, ManagementConsole manCon, ProjectDashboard projectDashboard) {
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
		    }
			});
	}
	
	public void importProjectSettings(ProjectSettings settings, String[] apps){
		for (int i=0; i<apps.length; i++){
			int row = 0;
			//Create header for app
			Label appName = new Label();
			appName.setText(apps[i]);
			appName.addStyleName("SettingsAppName");
			formContainer.setWidget(row++, 0, appName);
			//Get list of settings for app
			String[] set = settings.getAppSettings(apps[i]).split(";;;\\s*");
			for (int j=0; j<set.length; j++){
				String[] parts = set[j].split(",\\s*");
				
				if (parts[2].equals("char")){
					TextBox setting = new TextBox();
					setting.setName(apps[i]+"-"+parts[0]);
					//Check default value
					if (parts.length > 3){
						Window.alert("gotcha");
						setting.setValue(parts[3]);
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
						setting.setValue(parts[3]);
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
				}				
			}
			formContainer.setHTML(row, 0, "<hr width=\"90%\">");
			formContainer.getFlexCellFormatter().setColSpan(row++, 0, 2);

		}
		formContainer.setWidget(formContainer.getRowCount(), 0, new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
	}
	
	public void setActive(boolean active){
		this.active = active;
		if(!active){
			WarningLabel.setText("You must fill out all the settings and click \"Activate\" button in order start using project.");
			WarningLabel.setStyleName(style.WarningLabel());
		} else {
			WarningLabel.setText("");
			ActivateButton.setText("Deactivate");
			//SaveButton.
			//Button.setText("Submit");
		}
	}
	
	@UiHandler("SaveButton")
	void handleSaveButton(ClickEvent event){
		//optionsForm.add(formContainer);
		//projectDashboard.getDeckPanel().add(optionsForm);
		optionsForm.submit();
	}
	@UiHandler("ActivateButton")
	void handleActivateButton(ClickEvent event){
		TextBox a = new TextBox();
		a.setVisible(false);
		a.setName("active");
		if(this.active) {
			a.setText("false");
		} else {
			a.setText("true");
		}
		formContainer.setWidget(formContainer.getRowCount(), 1, a);
		//optionsForm.add(formContainer);

		//projectDashboard.getDeckPanel().add(optionsForm);
		optionsForm.submit();
	}
	public final native ProjectSettings asProjectSettings(JavaScriptObject jso) /*-{
		alert("ssss");
		return jso;
	}-*/;

}
