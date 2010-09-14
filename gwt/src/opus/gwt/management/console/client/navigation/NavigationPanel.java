package opus.gwt.management.console.client.navigation;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

public class NavigationPanel extends Composite {

	private static NavigationPanelUiBinder uiBinder = GWT.create(NavigationPanelUiBinder.class);
	interface NavigationPanelUiBinder extends UiBinder<Widget, NavigationPanel> {}

	private final String logoutURL = "/accounts/logout/";
	
	@UiField Button logoutButton;
	@UiField FormPanel logoutForm;	
	
	
	public NavigationPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		setupLogoutForm();
	}
	
	private void setupLogoutForm(){
		logoutForm.setMethod(FormPanel.METHOD_GET);
		logoutForm.setAction(logoutURL);
		logoutForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		    	  Window.Location.reload();
		      }
		 });
	}
	
	@UiHandler("logoutButton")
	void handleLogoutButton(ClickEvent event){
		logoutForm.submit();
	}

}
