package opus.gwt.management.console.client.appbrowser;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.ui.RootPanel;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class OpusCommunityApplicationBrowser implements EntryPoint {
	/**
	 * The message displayed to the user when the server cannot be reached or
	 * returns an error.
	 */
	private static final String SERVER_ERROR = "An error occurred while "
			+ "attempting to contact the server. Please check your network "
			+ "connection and try again.";

	private AppBrowserUiBinder appBrowser;// = new AppBrowserUiBinder();
	/**
	 * This is the entry point method.
	 */
	public void onModuleLoad() {
		RootPanel.get("main").add(appBrowser);
	}
}