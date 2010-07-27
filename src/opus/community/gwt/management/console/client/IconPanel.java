package opus.community.gwt.management.console.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class IconPanel extends Composite {

	private static IconPanelUiBinder uiBinder = GWT
			.create(IconPanelUiBinder.class);

	interface IconPanelUiBinder extends UiBinder<Widget, IconPanel> {
	}

	@UiField ScrollPanel iconScrollPanel;

	public IconPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}

}
