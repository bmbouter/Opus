package opus.gwt.management.console.client.resources;

import com.google.gwt.resources.client.CssResource;
import com.google.gwt.user.client.ui.Widget;

public class BreadCrumbCss extends Widget {
	public interface BreadCrumbStyle extends CssResource {
		String inactive();
		String active();
	}
}