package opus.gwt.management.console.client.event;

import java.util.HashMap;

import opus.gwt.management.console.client.overlays.DjangoPackage;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class GetDjangoPackagesEvent extends GwtEvent<GetDjangoPackagesEventHandler> {
	
	public static Type<GetDjangoPackagesEventHandler> TYPE = new Type<GetDjangoPackagesEventHandler>();
	private JsArray<DjangoPackage> djangoPackagesArray;
	private HashMap<String,DjangoPackage> djangoPackagesMap = new HashMap<String, DjangoPackage>();
	
	public GetDjangoPackagesEvent(JavaScriptObject djangoPackages){
		this.djangoPackagesArray = ConvertDjangoPackages(djangoPackages);
		processdjangoPackages();
	}
	
	private void processdjangoPackages() {
		for(int i = 0; i < djangoPackagesArray.length(); i++) {
			DjangoPackage dp = djangoPackagesArray.get(i);
			djangoPackagesMap.put(dp.getAppName(), dp);
		}
	}
	
	public HashMap<String, DjangoPackage> getDjangoPackages(){
		return djangoPackagesMap;
	}
	
  	@Override
  	public Type<GetDjangoPackagesEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(GetDjangoPackagesEventHandler handler) {
	  handler.onGetDjangoPackages(this);
  	}
  	
	public final native JsArray<DjangoPackage> ConvertDjangoPackages(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}
