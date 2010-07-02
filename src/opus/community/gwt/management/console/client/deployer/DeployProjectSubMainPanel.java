package opus.community.gwt.management.console.client.deployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class DeployProjectSubMainPanel extends Composite {

	private static DeployProjectSubMainPanelUiBinder uiBinder = GWT
			.create(DeployProjectSubMainPanelUiBinder.class);

	interface DeployProjectSubMainPanelUiBinder extends
			UiBinder<Widget, DeployProjectSubMainPanel> {
	}

	public DeployProjectSubMainPanel(String firstName) {
		initWidget(uiBinder.createAndBindUi(this));
	}
}
