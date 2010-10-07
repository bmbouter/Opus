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
	
	public void setText(String html) {
		text.setHTML(html);
	}
	
	public void setRed() {
		content.setStyleName(style.tooltip_right_red());
		arrow.setStyleName(style.tooltip_left_red());
	}
	
	public void setGray() {
		content.setStyleName(style.tooltip_right());
		arrow.setStyleName(style.tooltip_left());
	}
}
