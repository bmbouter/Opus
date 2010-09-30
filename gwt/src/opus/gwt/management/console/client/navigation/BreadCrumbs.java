package opus.gwt.management.console.client.navigation;

import java.util.HashMap;

import opus.gwt.management.console.client.resources.BreadCrumbCss.BreadCrumbStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class BreadCrumbs extends Composite {

	private static BreadCrumbsUiBinder uiBinder = GWT.create(BreadCrumbsUiBinder.class);
	interface BreadCrumbsUiBinder extends UiBinder<Widget, BreadCrumbs> {}
	
	private Label activeCrumb;
	private HashMap<String, Label> breadCrumbLabels;
	
	@UiField FlowPanel breadCrumbsContainer;
	@UiField BreadCrumbStyle style;
	
	public BreadCrumbs() {
		initWidget(uiBinder.createAndBindUi(this));
		activeCrumb = new Label();
		breadCrumbLabels = new HashMap<String, Label>();
	}

	public void setBreadCrumbs(String[] names){
		for(int i = 0; i < names.length; i++ ){
			if( i == names.length - 1){
				addBreadCrumb(names[i], true);
			} else {
				addBreadCrumb(names[i], false);
			}
		}
	}
	
	public void setInitialActiveCrumb(String name){
		activeCrumb = breadCrumbLabels.get(name);
	}
	
	private void addBreadCrumb(String name, boolean isLastCrumb){
		Label crumb = new Label();
		if( isLastCrumb ){
			crumb.setText(name);
		} else {
			crumb.setText(name + "     >");
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
	
	public void setActiveCrumb(String name){
		Label crumb = breadCrumbLabels.get(name);
		activeCrumb.setStyleName(style.inactive());
		crumb.setStyleName(style.active());
		activeCrumb = crumb; 
	}
}
