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
	private Label activeCrumb;
	private HashMap<String, Label> breadCrumbLabels;
	
	@UiField FlowPanel breadCrumbsContainer;
	@UiField BreadCrumbsPanelStyle style;
	
	public BreadCrumbsPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		activeCrumb = new Label();
		breadCrumbLabels = new HashMap<String, Label>();	
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
					}
		}});
	}
	
	public void setBreadCrumbs(String[] names){
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
	
	public void addBreadCrumb(String name, boolean isFirstCrumb){
		Label crumb = new Label();
		if( isFirstCrumb ){
			crumb.setText(name);
		} else {
			crumb.setText(">    " + name);
		}
		crumb.setStyleName(style.inactive());
		breadCrumbLabels.put(name, crumb);
		breadCrumbsContainer.add(crumb);
	}

	private void addBreadCrumb(String name){
		HTML crumb = new HTML();
		crumb.setHTML("<span>" + name + "</span> &raquo;");
		//Label crumb = new Label();
		crumb.setText(name + " > ");
		crumb.setStyleName(style.inactive());
		breadCrumbLabels.put(name, crumb);
		breadCrumbsContainer.add(crumb);
	}
	
	private void setActiveCrumb(String name){
		Label crumb = breadCrumbLabels.get(name);
		activeCrumb.setStyleName(style.inactive());
		crumb.setStyleName(style.active());
		activeCrumb = crumb; 
	}
}
