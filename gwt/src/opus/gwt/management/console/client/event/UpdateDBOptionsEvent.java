package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.DBOptions;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateDBOptionsEvent extends GwtEvent<UpdateDBOptionsEventHandler> {
	
	public static Type<UpdateDBOptionsEventHandler> TYPE = new Type<UpdateDBOptionsEventHandler>();
	private DBOptions dbOptions;
	
	public UpdateDBOptionsEvent(JavaScriptObject jso){
		this.dbOptions = ConvertDBOptionsData(jso);
	}
	
	public DBOptions getDBOptionsData(){
		return dbOptions;
	}
	
  	@Override
  	public Type<UpdateDBOptionsEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateDBOptionsEventHandler handler) {
	  handler.onUpdateDBOptions(this);
  	}
	
	public final native DBOptions ConvertDBOptionsData(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}