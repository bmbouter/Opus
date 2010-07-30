package opus.community.gwt.management.console.client.deployer;

import opus.community.gwt.management.console.client.resources.ApplicationPopupCss.ApplicationPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AddOtherApplication extends Composite {

	private static AddOtherApplicationUiBinder uiBinder = GWT
			.create(AddOtherApplicationUiBinder.class);

	interface AddOtherApplicationUiBinder extends
			UiBinder<Widget, AddOtherApplication> {
	}
	@UiField 
	ApplicationPopupStyle style;
		
	@UiField
	TextBox applicationNameTextBox;
	
	@UiField 
	TextBox applicationURLTextBox;

	@UiField 
	Button addApplicationButton;
	
	@UiField
	PopupPanel otherApplicationPopup;
	
	@UiField
	ListBox appTypeListBox;
	
	private AddAppsBuildProject appBuilder;
	
	public AddOtherApplication(AddAppsBuildProject appBuilder) {
		//initWidget(uiBinder.createAndBindUi(this));
	
		AddOtherApplicationUiBinder uiBinder = GWT.create(AddOtherApplicationUiBinder.class);
	    uiBinder.createAndBindUi(this);
	    otherApplicationPopup.setAutoHideEnabled(true);
	    otherApplicationPopup.hide();
	    otherApplicationPopup.setGlassEnabled(true);
	    otherApplicationPopup.setGlassStyleName(style.applicationPopupGlass());
	    otherApplicationPopup.addCloseHandler(new CloseHandler<PopupPanel>(){
	    	@Override
	    	public void onClose(CloseEvent<PopupPanel> event) {
	    		applicationNameTextBox.setText("");
	    		applicationURLTextBox.setText("");
	    	}
	    });
	    appTypeListBox.addItem("Git Repository", "git");
	    appTypeListBox.addItem("Local File", "file");
	    this.appBuilder = appBuilder;
	}
	
	public void show() {
		otherApplicationPopup.center();
		otherApplicationPopup.show();
	}

	public void hide() {
		otherApplicationPopup.hide();
	}

	@UiHandler("addApplicationButton")
	void onClick(ClickEvent e) {
		
		final String appString = applicationNameTextBox.getText();
		final String appPath = applicationURLTextBox.getText();
		final String appType = appTypeListBox.getValue(appTypeListBox.getSelectedIndex());
		appBuilder.addApp(appString, appPath, appType);
    	this.hide();
	}

}
