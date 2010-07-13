package opus.community.gwt.management.console.client.deployer;

import opus.community.gwt.management.console.client.resources.ApplicationPopupCss.ApplicationPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class ApplicationDetailDialog extends Composite {

	private static ApplicationDetailInformationUiBinder uiBinder = GWT
			.create(ApplicationDetailInformationUiBinder.class);

	interface ApplicationDetailInformationUiBinder extends
			UiBinder<Widget, ApplicationDetailDialog> {
	}


	 @UiField PopupPanel applicationPopup;
	 @UiField FlexTable versionsFlexTable;
	 @UiField ApplicationPopupStyle style;
	  
	 
	  public ApplicationDetailDialog() {
		ApplicationDetailInformationUiBinder uiBinder = GWT.create(ApplicationDetailInformationUiBinder.class);
	    uiBinder.createAndBindUi(this);
	    applicationPopup.setAutoHideEnabled(true);
	    applicationPopup.hide();
	    applicationPopup.setGlassEnabled(true);
	    applicationPopup.setGlassStyleName(style.applicationPopupGlass());
	  }

	  public void show() {
		 applicationPopup.center();
		 applicationPopup.show();
	  }

	  public void hide() {
		  applicationPopup.hide();
	  }
	/*  @UiHandler("cancelButton")
	  void onClick(ClickEvent e) {
		  applicationPopup.hide();
	  }*/

}
