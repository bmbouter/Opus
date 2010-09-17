package opus.gwt.management.console.client.tools;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class TooltipPanel extends PopupPanel {
	private static TooltipPanelUiBinder uiBinder = GWT.create(TooltipPanelUiBinder.class);
	interface TooltipPanelUiBinder extends UiBinder<Widget, TooltipPanel> {}
	
	@UiField HTML text;

	public TooltipPanel() {
		super();
		setWidget(uiBinder.createAndBindUi(this));
		setAutoHideEnabled(true);
	}
	
	public void setText(String html) {
		text.setHTML(html);
	}
}
