package opus.gwt.management.console.client.tools;

import opus.gwt.management.console.client.deployer.AppIcon;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.MouseOutEvent;
import com.google.gwt.event.dom.client.MouseOutHandler;
import com.google.gwt.event.dom.client.MouseOverEvent;
import com.google.gwt.event.dom.client.MouseOverHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class DescriptionPanel extends PopupPanel {
	private static DescriptionPanelUiBinder uiBinder = GWT
			.create(DescriptionPanelUiBinder.class);

	interface DescriptionPanelUiBinder extends
			UiBinder<Widget, DescriptionPanel> {
	}
	
	private static DescriptionPanel instance;
	
	@UiField Label title;
	@UiField Label text;
	
	public DescriptionPanel() {
		super(true);
		setWidget(uiBinder.createAndBindUi(this));
	}
	
	public static DescriptionPanel getInstance() {
		if(instance == null) {
			return new DescriptionPanel();
		} else {
			return instance;
		}
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
	
	public void addMouseOverHandler(MouseOverHandler handler) {
		this.addDomHandler(handler, MouseOverEvent.getType());
	}
	
	public void addMouseOutHandler(MouseOutHandler handler) {
		this.addDomHandler(handler, MouseOutEvent.getType());
	}
}
