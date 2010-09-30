package opus.gwt.management.console.client.event;

import opus.gwt.management.console.client.overlays.ProjectData;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.shared.GwtEvent;


public class ImportAppListEvent extends GwtEvent<ImportAppListEventHandler> {
	
	public static Type<ImportAppListEventHandler> TYPE = new Type<ImportAppListEventHandler>();
	private JsArray<ProjectData> projectData;
	
	public ImportAppListEvent(JavaScriptObject jso){
		this.projectData = ConvertProjectData(jso);
	}
	
	public JsArray<ProjectData> getProjectData(){
		return projectData;
	}
	
  	@Override
  	public Type<ImportAppListEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(ImportAppListEventHandler handler) {
	  handler.onImportAppList(this);
  	}
	
	public final native JsArray<ProjectData> ConvertProjectData(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
}