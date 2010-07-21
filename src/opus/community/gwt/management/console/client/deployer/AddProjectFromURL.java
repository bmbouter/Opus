package opus.community.gwt.management.console.client.deployer;

import opus.community.gwt.management.console.client.deployer.AddOtherApplication.AddOtherApplicationUiBinder;
import opus.community.gwt.management.console.client.resources.ApplicationPopupCss.ApplicationPopupStyle;
import opus.community.gwt.management.console.client.resources.ProjectURLPopupCss.ProjectURLPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AddProjectFromURL extends Composite {

	private static AddProjectFromURLUiBinder uiBinder = GWT
			.create(AddProjectFromURLUiBinder.class);

	interface AddProjectFromURLUiBinder extends
			UiBinder<Widget, AddProjectFromURL> {
	}
	@UiField 
	ProjectURLPopupStyle style;
	@UiField
	Button addProjectFromURLButton;
	@UiField
	PopupPanel addProjectFromURLPopup;
	@UiField 
	TextBox projectURLTextBox;
	
	private AddAppsBuildProject appBuilder;
	
	public AddProjectFromURL(AddAppsBuildProject appBuilder) {
		//initWidget(uiBinder.createAndBindUi(this));
		
		AddProjectFromURLUiBinder uiBinder = GWT.create(AddProjectFromURLUiBinder.class);
	    uiBinder.createAndBindUi(this);
	    addProjectFromURLPopup.setAutoHideEnabled(true);
	    addProjectFromURLPopup.hide();
	    addProjectFromURLPopup.setGlassEnabled(true);
	    addProjectFromURLPopup.setGlassStyleName(style.applicationPopupGlass());
	    addProjectFromURLPopup.addCloseHandler(new CloseHandler<PopupPanel>(){
	    	@Override
	    	public void onClose(CloseEvent<PopupPanel> event) {
	    		projectURLTextBox.setText("");
	    	}
	    });
	    this.appBuilder = appBuilder;
	}
	
	public void show() {
		addProjectFromURLPopup.center();
		addProjectFromURLPopup.show();
	}

	public void hide() {
		addProjectFromURLPopup.hide();
	}

	@UiHandler("addProjectFromURLButton")
	void onClick(ClickEvent e) {
		
		final String urlString = projectURLTextBox.getText()+"/?callback=";
		appBuilder.addProject(URL.encode(urlString));
    	this.hide();
	  
	}
}
