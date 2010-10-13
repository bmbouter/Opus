package opus.gwt.management.console.client.navigation;

import java.util.HashMap;

import opus.gwt.management.console.client.event.BreadCrumbEvent;
import opus.gwt.management.console.client.event.BreadCrumbEventHandler;
import opus.gwt.management.console.client.resources.BreadCrumbsPanelCss.BreadCrumbsPanelStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class BreadCrumbsPanel extends Composite {

	private static BreadCrumbsUiBinder uiBinder = GWT.create(BreadCrumbsUiBinder.class);
	interface BreadCrumbsUiBinder extends UiBinder<Widget, BreadCrumbsPanel> {}
	
	private HandlerManager eventBus;
	private HTML activeCrumb;
	private HashMap<String, HTML> breadCrumbLabels;
	
	@UiField FlowPanel breadCrumbsContainer;
	@UiField BreadCrumbsPanelStyle style;
	
	public BreadCrumbsPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		activeCrumb = new HTML();
		breadCrumbLabels = new HashMap<String, HTML>();	
	}

	public void setEventBus(HandlerManager eventBus){
		this.eventBus = eventBus;
		registerHandlers();
	}
	
	private void registerHandlers(){
		eventBus.addHandler(BreadCrumbEvent.TYPE, 
			new BreadCrumbEventHandler(){
				public void onBreadCrumb(BreadCrumbEvent event){
					if( event.getAction() == BreadCrumbEvent.Action.SET_CRUMBS ){
						setBreadCrumbs(event.getCrumbNames());
					} else if( event.getAction() == BreadCrumbEvent.Action.SET_ACTIVE ){
						setActiveCrumb(event.getCrumb());
					} else if( event.getAction() == BreadCrumbEvent.Action.ADD_CRUMB ){
						setActiveCrumb(event.getCrumb());
					} else if( event.getAction() == BreadCrumbEvent.Action.REMOVE_CRUMB ){
						removeBreadCrumb();
					}
		}});
	}
	
	private void setBreadCrumbs(String[] names){
		breadCrumbsContainer.clear();
		breadCrumbLabels.clear();
		for(int i = 0; i < names.length; i++ ){
			if( i == 0 ){
				addBreadCrumb(names[i], true);
			} else {
				addBreadCrumb(names[i], false);
			} 
			if( i == 0 ){
				setActiveCrumb(names[0]);
			}
		}
	}
	
	private void addBreadCrumb(String name, boolean isFirstCrumb){
		HTML crumb = new HTML();
		if( isFirstCrumb ){
			crumb.setText(name);
		} else {
			crumb.setHTML("&raquo; " + name);
		}
		crumb.setStyleName(style.inactive());
		breadCrumbLabels.put(name, crumb);
		breadCrumbsContainer.add(crumb);
	}

	private void removeBreadCrumb(){
		breadCrumbsContainer.remove(breadCrumbLabels.size());
	}
	
	private void setActiveCrumb(String name){
		HTML crumb = breadCrumbLabels.get(name);
		activeCrumb.setStyleName(style.inactive());
		crumb.setStyleName(style.active());
		activeCrumb = crumb; 
	}
}
