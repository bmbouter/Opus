package opus.community.gwt.management.console.client.deployer;

import java.util.ArrayList;

import opus.community.gwt.management.console.client.deployer.ApplicationDetailDialog.ApplicationDetailInformationUiBinder;
import opus.community.gwt.management.console.client.resources.ApplicationPopupCss.ApplicationPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
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
	
	private AddAppsBuildProject appBuilder;
	
	public AddOtherApplication(AddAppsBuildProject appBuilder) {
		//initWidget(uiBinder.createAndBindUi(this));
	
		AddOtherApplicationUiBinder uiBinder = GWT.create(AddOtherApplicationUiBinder.class);
	    uiBinder.createAndBindUi(this);
	    otherApplicationPopup.setAutoHideEnabled(true);
	    otherApplicationPopup.hide();
	    otherApplicationPopup.setGlassEnabled(true);
	    otherApplicationPopup.setGlassStyleName(style.applicationPopupGlass());
	    
	    this.appBuilder = appBuilder;
		
		//	button.setText(firstName);
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
		appBuilder.addApp(appString, appPath);
		applicationNameTextBox.setText("");
		applicationURLTextBox.setText("");
    	this.hide();
	  
	}

}
