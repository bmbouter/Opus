package opus.gwt.management.console.client.tools;

import opus.gwt.management.console.client.resources.TooltipPanelCss.TooltipPanelStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class TooltipPanel extends PopupPanel {
	private static TooltipPanelUiBinder uiBinder = GWT.create(TooltipPanelUiBinder.class);
	interface TooltipPanelUiBinder extends UiBinder<Widget, TooltipPanel> {}
	
	@UiField HTML text;
	@UiField HTMLPanel content;
	@UiField HTMLPanel arrow;
	@UiField TooltipPanelStyle style;

	public TooltipPanel() {
		super();
		setWidget(uiBinder.createAndBindUi(this));
		setAutoHideEnabled(true);
	}
	
	/**
	 * Set the text to a certain String
	 * @param html the String to use; can contain HTML
	 */
	public void setText(String html) {
		text.setHTML(html);
	}
	
	/**
	 * Set the tooltip to a red color; typically used for errors
	 */
	public void setRed() {
		content.setStyleName(style.tooltip_right_red());
		arrow.setStyleName(style.tooltip_left_red());
	}
	
	/**
	 * Set the tooltip to a gray color; default color
	 */
	public void setGray() {
		content.setStyleName(style.tooltip_right());
		arrow.setStyleName(style.tooltip_left());
	}
}
