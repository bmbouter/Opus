package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;
import com.google.gwt.user.client.ui.Widget;


public class PanelTransitionEvent extends GwtEvent<PanelTransitionEventHandler> {
	
	public static Type<PanelTransitionEventHandler> TYPE = new Type<PanelTransitionEventHandler>();
	private String transitionType;
	private Widget panel;
	
	public PanelTransitionEvent(String transitionType, Widget panel){
		this.transitionType = transitionType;
		this.panel = panel;
	}

	public PanelTransitionEvent(String transitionType){
		this.transitionType = transitionType;
	}

	
	public String getTransitionType(){
		return transitionType;
	}
	
	public Widget getPanel(){
		return panel;
	}
	
  	@Override
  	public Type<PanelTransitionEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(PanelTransitionEventHandler handler) {
	  handler.onPanelTransition(this);
  	}
}