package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;
import com.google.gwt.user.client.ui.Widget;


public class PanelTransitionEvent extends GwtEvent<PanelTransitionEventHandler> {
	
	public static Type<PanelTransitionEventHandler> TYPE = new Type<PanelTransitionEventHandler>();
	//private String transitionType;
	private Widget panel;
	public enum TransitionTypes{PREVIOUS, NEXT, DELETE, SETTINGS, DEPLOY, PROJECTS, DASHBOARD};
	private TransitionTypes transitionType;
	public String name;
	
	public PanelTransitionEvent(TransitionTypes transitionType, Widget panel){
		this.transitionType = transitionType;
		this.panel = panel;
	}

	public PanelTransitionEvent(TransitionTypes transitionType){
		this.transitionType = transitionType;
	}

	public PanelTransitionEvent(TransitionTypes transitionType, String name){
		this.name = name;
		this.transitionType = transitionType;
	}
	
	public TransitionTypes getTransitionType(){
		return transitionType;
	}
	
	public Widget getPanel(){
		return panel;
	}
	
	public String getName(){
		return name;
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