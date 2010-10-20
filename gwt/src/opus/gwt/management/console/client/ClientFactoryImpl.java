package opus.gwt.management.console.client;

import com.google.gwt.event.shared.EventBus;
import com.google.gwt.event.shared.SimpleEventBus;

public class ClientFactoryImpl implements ClientFactory {
	private final EventBus eventBus = new SimpleEventBus();
	private final JSVariableHandler jsVarHandler = new JSVariableHandler();
	
	@Override
	public EventBus getEventBus(){
		return eventBus;
	}
	
	@Override
	public JSVariableHandler getJSVariableHandler(){
		return jsVarHandler;
	}
}
