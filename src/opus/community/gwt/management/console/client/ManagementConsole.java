package opus.community.gwt.management.console.client;

import opus.community.gwt.management.console.client.deployer.applicationDeployer;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.RootLayoutPanel;
import com.google.gwt.user.client.ui.Widget;

public class ManagementConsole extends Composite {

	private static ManagementConsoleUiBinder uiBinder = GWT
			.create(ManagementConsoleUiBinder.class);

	interface ManagementConsoleUiBinder extends
			UiBinder<Widget, ManagementConsole> {
	}

	private applicationDeployer appDeployer = new applicationDeployer(); 
	
	@UiField RootLayoutPanel root;
	
	public ManagementConsole() {
		initWidget(uiBinder.createAndBindUi(this));
		root.add(appDeployer);
	}
}
