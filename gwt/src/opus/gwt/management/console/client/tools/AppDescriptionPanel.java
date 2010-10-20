package opus.gwt.management.console.client.tools;

import opus.gwt.management.console.client.deployer.AppIcon;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class AppDescriptionPanel extends PopupPanel {
	private static AppDescriptionPanelUiBinder uiBinder = GWT
			.create(AppDescriptionPanelUiBinder.class);

	interface AppDescriptionPanelUiBinder extends
			UiBinder<Widget, AppDescriptionPanel> {
	}
	
	@UiField Label title;
	@UiField Label text;
	
	public AppDescriptionPanel() {
		super();
		setWidget(uiBinder.createAndBindUi(this));
		setAutoHideEnabled(true);
	}
	
	public void setTitle(AppIcon icon) {
		title.setText(icon.getAppName());
	}
	
	public void setTitle(String str) {
		title.setText(str);
	}
	
	public void setText(AppIcon icon) {
		text.setText(icon.getDescription());
	}
	
	public void setText(String str) {
		text.setText(str);
	}
}
