package opus.gwt.management.console.client.event;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.shared.GwtEvent;


public class UpdateFeaturedListEvent extends GwtEvent<UpdateFeaturedListEventHandler> {
	
	public static Type<UpdateFeaturedListEventHandler> TYPE = new Type<UpdateFeaturedListEventHandler>();
	private JavaScriptObject featuredList;
	
	public UpdateFeaturedListEvent(JavaScriptObject featuredList){
		this.featuredList = featuredList;
	}
	
	public JavaScriptObject getFeaturedList(){
		return featuredList;
	}
	
  	@Override
  	public Type<UpdateFeaturedListEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(UpdateFeaturedListEventHandler handler) {
	  handler.onUpdateFeaturedList(this);
  	}
}