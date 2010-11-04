package opus.gwt.management.console.client.event;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import opus.gwt.management.console.client.overlays.DjangoPackage;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;
import com.google.gwt.user.client.Window;


public class GetDjangoPackagesEvent extends GwtEvent<GetDjangoPackagesEventHandler> {
	
	public static Type<GetDjangoPackagesEventHandler> TYPE = new Type<GetDjangoPackagesEventHandler>();
	private JsArray<DjangoPackage> djangoPackagesArray;
	private List<DjangoPackage> djangoPackagesMap = new ArrayList<DjangoPackage>();
	
	public GetDjangoPackagesEvent(JavaScriptObject djangoPackages){
		this.djangoPackagesArray = ConvertDjangoPackages(djangoPackages);
		processDjangoPackages();
	}
	
	private void processDjangoPackages() {
		for(int i = 0; i < djangoPackagesArray.length(); i++) {
			DjangoPackage dp = djangoPackagesArray.get(i);
			djangoPackagesMap.add(dp.getPk() - 1, dp);
		}
	}
	
	public List<DjangoPackage> getDjangoPackages(){
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
