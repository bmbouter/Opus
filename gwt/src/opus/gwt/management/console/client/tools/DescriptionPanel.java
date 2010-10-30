package opus.gwt.management.console.client.tools;

import opus.gwt.management.console.client.overlays.Application;

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
	
	/**
	 * Return an instance of the DescriptionPanel
	 * NOTE: This isnt necessary for a functioning DescriptionPanel
	 * @return an instance of the DescriptionPanel
	 */
	public static DescriptionPanel getInstance() {
		if(instance == null) {
			return new DescriptionPanel();
		} else {
			return instance;
		}
	}
	
	/**
	 * Set the title that is displayed using an application
	 * @param app the application to use
	 */
	public void setTitle(Application app) {
		title.setText(app.getAppName());
	}
	
	/**
	 * Set the title that is displayed to a certain String
	 * @param str the String title to set
	 */
	public void setTitle(String str) {
		title.setText(str);
	}
	
	/**
	 * Set the description that is displayed using an application
	 * @param app the application to use
	 */
	public void setText(Application app) {
		text.setText(app.getDescription());
	}
	
	/**
	 * Set the description that is displayed to a certain String
	 * @param str the String description to set
	 */
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
