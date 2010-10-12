package opus.gwt.management.console.client.resources;

import com.google.gwt.resources.client.CssResource;
import com.google.gwt.user.client.ui.Widget;


public class NavigationPanelCss extends Widget {
	  public interface NavigationPanelStyle extends CssResource {
		  String active();
		  String topProjectsButtonActive();
		  String projectsPopup();
		  String lastLabel();
		  String popupLabelActive();
		  String popupLabel();
		  String button();
	  }
}