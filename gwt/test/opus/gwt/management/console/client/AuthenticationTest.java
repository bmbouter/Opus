package opus.gwt.management.console.client;

import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.junit.client.GWTTestCase;

public class AuthenticationTest extends GWTTestCase {

	@Override
	public String getModuleName() {
		return null;
	}
	
	public void testAuthentication(){
		HandlerManager eventBus = new HandlerManager(null);
		AuthenticationPanel authenticationPanel = new AuthenticationPanel(eventBus);
		
		
	}
}
