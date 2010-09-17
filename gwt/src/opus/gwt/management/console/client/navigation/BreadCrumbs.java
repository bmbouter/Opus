package opus.gwt.management.console.client.navigation;

import opus.gwt.management.console.client.resources.BreadCrumbCss.BreadCrumbStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class BreadCrumbs extends Composite {

	private static BreadCrumbsUiBinder uiBinder = GWT.create(BreadCrumbsUiBinder.class);
	interface BreadCrumbsUiBinder extends UiBinder<Widget, BreadCrumbs> {}
	
	private Label activeCrumb;
	
	@UiField FlowPanel breadCrumbsContainer;
	@UiField BreadCrumbStyle style;
	
	public BreadCrumbs() {
		initWidget(uiBinder.createAndBindUi(this));
		activeCrumb = new Label();
	}

	public void setBreadCrumbs(String[] names){
		for(String name : names){
			addBreadCrumb(name);
		}
	}
	
	public void setInitialActiveCrumb(String name){
		
	}
	
	private void addBreadCrumb(String name){
		Label crumb = new Label();
		crumb.setText(name + "  >  ");
		crumb.setStyleName(style.inactive());
		breadCrumbsContainer.add(crumb);
	}
	
	public void setActiveCrumb(String name){
		Window.alert(name);
	}
	
}
