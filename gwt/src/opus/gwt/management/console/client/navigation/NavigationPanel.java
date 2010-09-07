package opus.gwt.management.console.client.navigation;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class NavigationPanel extends Composite {

	private static NavigationPanelUiBinder uiBinder = GWT.create(NavigationPanelUiBinder.class);
	interface NavigationPanelUiBinder extends UiBinder<Widget, NavigationPanel> {}


	public NavigationPanel() {
		initWidget(uiBinder.createAndBindUi(this));

	}

}
