package opus.community.gwt.management.console.client.deployer;

import java.util.ResourceBundle;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.ui.RootPanel;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class ApplicationDeployerGWT implements EntryPoint {
	/**
	 * The message displayed to the user when the server cannot be reached or
	 * returns an error.
	 */
	private static final String SERVER_ERROR = "An error occurred while "
			+ "attempting to contact the server. Please check your network "
			+ "connection and try again.";

	private applicationDeployer deployer = new applicationDeployer();
	
	/**
	 * This is the entry point method.
	 */
	public void onModuleLoad() {
		RootPanel.get().add(deployer);
	}
	

}
