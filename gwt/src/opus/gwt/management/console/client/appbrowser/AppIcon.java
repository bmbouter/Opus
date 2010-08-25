package opus.gwt.management.console.client.appbrowser;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class AppIcon extends Composite {

	private static AppIconUiBinder uiBinder = GWT.create(AppIconUiBinder.class);

	interface AppIconUiBinder extends UiBinder<Widget, AppIcon> {
	}

	@UiField
	FocusPanel iconPanel;
	@UiField
	HTML iconHTML;
	
	private String name;
	private String icon;
	private String path;
	private String desc;
	private String pk;
	private JsArray <VersionData> versions;
	private JSVariableHandler JSVarHandler;
	private FormPanel versionForm;
	private VerticalPanel formContainer;
	private int selectedVersion;

	public AppIcon(String name, String iconURL, String description, int pk, String path) {
		initWidget(uiBinder.createAndBindUi(this));
		JSVarHandler = new JSVariableHandler();
		versionForm = new FormPanel();
		formContainer = new VerticalPanel();
		versionForm.add(formContainer);
		this.name = name;
		this.icon = iconURL;
		this.desc = description;
		this.path = path;
		this.pk = String.valueOf(pk);
	}
	
	public void setIconHTML(String html) {
		iconHTML.setHTML(html);
	}
	
	public String getName(){
		return this.name;
	}
	
	public String getIcon() {
		return this.icon;
	}
	
	public String getDescription(){
		return this.desc;
	}
	
	public String getShortDescription(){
		if(this.desc.length() > 75) {
			return this.desc.substring(0, 75);
		} else {
			return this.desc;
		}
	}
	
	public String getPath() {
		String fullpath = path+versions.get(selectedVersion).getTag();
		return fullpath;
	}
	
	public FormPanel getVersions(){
		return this.versionForm;
	}
	
	public String getSelectedVersionPk(){
		return versions.get(selectedVersion).getPk();
	}
	
	public void setSelectedVersion(int pk){
		for (int i=0; i<versions.length(); i++){
			if (Integer.valueOf(versions.get(i).getPk()) == pk){
				selectedVersion = i;
				i = versions.length();
			}
		}
	}
	
	public String getAppPk(){
		return this.pk;
	}
	
	public String getType() {
		return "git";
	}
	
	
	public void handleVersionInfo(JsArray <VersionData> data){
		//Window.alert(String.valueOf(data.length()));
		formContainer.add(new HTML("Versions:"));
		for (int i=0; i<data.length(); i++){
			final int j = i;
			//Window.alert(String.valueOf(i));
			RadioButton button = new RadioButton("versions");
			button.setFormValue(String.valueOf(i));
			if (i == 0) {
				button.setValue(true);
			}
			button.setText(data.get(i).getVersion());
			formContainer.add(button);
			button.addClickHandler(new ClickHandler() {
		        public void onClick(ClickEvent event) {
		        	selectedVersion = j;
		        	
		        }
			});
		}
		
		this.versions = data;
	}
	
	public void whatIsSelected(){
		Window.alert(String.valueOf(selectedVersion));
	}
	
	public final native JsArray<VersionData> asArrayOfVersionData(JavaScriptObject jso) /*-{
    	return jso;
	}-*/;
/*
	@UiHandler("button")
	void onClick(ClickEvent e) {
		Window.alert("Hello!");
	}
*/
	
	
}
