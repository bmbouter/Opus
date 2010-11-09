package opus.gwt.management.console.client.dashboard;

import java.util.ArrayList;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.event.PanelTransitionEvent;
import opus.gwt.management.console.client.event.PanelTransitionEventHandler;
import opus.gwt.management.console.client.overlays.Project;
import opus.gwt.management.console.client.overlays.ProjectSettingsData;
import opus.gwt.management.console.client.resources.FormsCss.FormsStyle;
import opus.gwt.management.console.client.tools.TooltipPanel;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.FocusHandler;
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
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AppSettingsPanel extends Composite {

	interface AppSettingsUiBinder extends UiBinder<Widget, AppSettingsPanel> {}
	private static AppSettingsUiBinder uiBinder = GWT.create(AppSettingsUiBinder.class);
	
	private final String optionsUrl = "/deployments/projectName/confapps/";
	
	private String projectName;
	private ClientFactory clientFactory;
	private JSVariableHandler jsVarHandler;
	private EventBus eventBus;
	private boolean active;
	private boolean hasSettings;
	private Project project;
	private TooltipPanel tooltip;

	@UiField Button saveButton;
	@UiField Button activateButton;
	@UiField Label projectLabel;
	@UiField FormsStyle form;
	@UiField FlowPanel content;


	public AppSettingsPanel(ClientFactory clientFactory) {
		initWidget(uiBinder.createAndBindUi(this));
		this.clientFactory = clientFactory;
		this.jsVarHandler = clientFactory.getJSVariableHandler();
		this.eventBus = clientFactory.getEventBus();
		registerHandlers();
		tooltip = new TooltipPanel();
		setTooltipInitialState();
	}
	
	private void registerHandlers() {
		eventBus.addHandler(PanelTransitionEvent.TYPE, 
				new PanelTransitionEventHandler(){
					public void onPanelTransition(PanelTransitionEvent event){
						if(event.getTransitionType() == PanelTransitionEvent.TransitionTypes.SETTINGS){
							projectLabel.setText(projectName + " settings: " + event.name);
							importProjectSettings(project.getAppSettings(), event.name);
						} else if(event.getTransitionType() == PanelTransitionEvent.TransitionTypes.DASHBOARD){
							projectName = event.name;
							project = clientFactory.getProjects().get(projectName);
						}
					}
			});
	}
	
	public void importProjectSettings(ProjectSettingsData settings, String application) {
		content.clear();
		content.setStyleName(form.content());
		
		JsArray<JavaScriptObject> appSettings = settings.getAppSettings(application);
		
		FlowPanel formWrapper = new FlowPanel();
		formWrapper.setStyleName(form.formWrapper());

		for(int j = 0; j < appSettings.length(); j++) {
			FlowPanel field = new FlowPanel();
			FlowPanel fieldWrapper = new FlowPanel();
			fieldWrapper.setStyleName(form.fieldWrapper());
			field.setStyleName(form.field());
			
			JsArray<JavaScriptObject> settingsArray = settings.getSettingsArray(appSettings.get(j));
			String choiceSettings = settings.getChoiceSettingsArray(appSettings.get(j));
			
			String[] settingsContent = settingsArray.join(";;").split(";;\\s*");
			//String[] choiceSettingsContent = choiceSettingsArray.join(";;").split(";;\\s*");
			
			Label appName = new Label(application);
			
			Label description = new Label(settingsContent[0]);
			description.setStyleName(form.settingsFieldLabel());
			field.add(description);
			
			if(settingsContent[2].equals("string")) {
				final TextBox setting = new TextBox();
				setting.setName(settingsContent[1]);
				setting.setStyleName(form.greyBorder());
				
				if(settingsContent.length > 3) {
					setting.setText(settingsContent[3]);
				}
				
				setting.addFocusHandler(new FocusHandler() {
					public void onFocus(FocusEvent event) {
						tooltip.hide();
						tooltip.setVisible(true);
						
						int x = getTooltipPosition(setting)[0];
						int y = getTooltipPosition(setting)[1];
							
						tooltip.setGray();
						setTooltipPosition(x, y);
						tooltip.show();
						setTooltipText(setting.getName());
					}
				});
				
				field.add(setting);
			} else if(settingsContent[2].equals("int")) {
				final TextBox setting = new TextBox();
				setting.setName(settingsContent[1]);
				setting.setStyleName(form.greyBorder());
				
				if(settingsContent.length > 3) {
					setting.setText(settingsContent[3]);
				}
				
				setting.addFocusHandler(new FocusHandler() {
					public void onFocus(FocusEvent event) {
						tooltip.hide();
						tooltip.setVisible(true);
						
						int x = getTooltipPosition(setting)[0];
						int y = getTooltipPosition(setting)[1];
							
						tooltip.setGray();
						setTooltipPosition(x, y);
						tooltip.show();
						setTooltipText(setting.getName());
					}
				});
				
				field.add(setting);
			} else if(settingsContent[2].equals("choice")) {
				ListBox setting = new ListBox();
				setting.setName(settingsContent[1]);
				setting.setStyleName(form.greyBorder());
				setting.getElement().setInnerHTML(choiceSettings);
				
				field.add(setting);
			} else if(settingsContent[2].equals("bool")) {
				CheckBox setting = new CheckBox();
				setting.setName(settingsContent[1]);
				
				if (settingsContent.length > 3) {
					setting.setValue(Boolean.valueOf(settingsContent[3]));
				}
			}

			fieldWrapper.add(field);
			formWrapper.add(fieldWrapper);
		}
		
		content.add(formWrapper);
	}
	
	public void setHasSettings(boolean state) {
		this.hasSettings = state;
	}
	
	//ProjectManagerController.displayOptions() calls this function  
//	public void setActive(boolean active){
//		this.active = active;
//		if(!active){
//			if(hasSettings){
//				WarningLabel.setText("You must fill out all the settings and click \"Save and Activate\" button in order start using project.");
//			} else {
//				WarningLabel.setText("This project is not active.  Press the Activate button to activate it.");
//				ActivateButton.setText("Activate");
//				SaveButton.setVisible(false);
//			}
//			WarningLabel.setStyleName(style.WarningLabel());
//		} else {
//			WarningLabel.setText("");
//			ActivateButton.setText("Deactivate");
//			SaveButton.setVisible(true);
//			//Button.setText("Submit");
//		}
//	}
	
//	private boolean validateForm(){
//		for(String t : textboxes){
//			//Window.alert(getValue(t));
//			if (DOM.getElementById(t).getInnerText().length() == 0) {
//				Window.alert("All settings are required.");
//				return false;
//			}
//		}
//		return true;
//	}
	
	public final native String getValue(String id) /*-{ 
		alert("hello");
		return document.getElementById(id).value; }-*/;
	
//	@UiHandler("SaveButton")
//	void handleSaveButton(ClickEvent event){
//		if( validateForm() ){
//
//			//formContainer.setWidget(formContainer.getRowCount(), 0, new Hidden("csrfmiddlewaretoken", jsVarHandler.getCSRFTokenURL()));
//			optionsForm.add(formContainer);
//			//optionsForm.submit();
//			
//			saveSettings();
//		}
//	}
	
	@UiHandler("activateButton")
	void handleActivateButton(ClickEvent event){
		saveSettings();
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
	
	/**
	 * Set the tooltips initial state on page load
	 */
	private void setTooltipInitialState() {
		tooltip.setVisible(false);
	}
	
	/**
	 * Set the position of a tooltip relative to the browser window
	 * @param x the x coordinate
	 * @param y the y coordinate
	 */
	private void setTooltipPosition(int x, int y) {
		tooltip.setPopupPosition(x, y);
	}
	
	/**
	 * Set the text of a tooltip
	 * @param text the text to set
	 */
	private void setTooltipText(String text) {
		tooltip.hide();
		tooltip.setText(text);
		tooltip.show();
	}
	
	/**
	 * Return the tooltip position as an array in for them [x, y]
	 * @param textbox the textbox to get the position of
	 * @return tooltip position
	 */
	private int[] getTooltipPosition(TextBox textbox) {
		int[] pos = new int[2];
		
		pos[0] = textbox.getAbsoluteLeft() + textbox.getOffsetWidth() + 5;
		pos[1] = textbox.getAbsoluteTop() + 2;
		
		return pos;
	}
	
	/**
	 * Return the tooltip position as an array in for them [x, y]
	 * @param textbox the textbox to get the position of
	 * @return tooltip position
	 */
	private int[] getTooltipPosition(PasswordTextBox textbox) {
		int[] pos = new int[2];
		
		pos[0] = textbox.getAbsoluteLeft() + textbox.getOffsetWidth() + 5;
		pos[1] = textbox.getAbsoluteTop() + 2;
	
		return pos;
	}
}
