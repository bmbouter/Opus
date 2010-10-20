package opus.gwt.management.console.client.resources.images;

import com.google.gwt.core.client.GWT;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.resources.client.DataResource;
import com.google.gwt.resources.client.ImageResource;


public interface OpusImages extends ClientBundle {
	OpusImages INSTANCE = GWT.create(OpusImages.class);
	
	public interface OpusImagesCssResource extends CssResource {
		String mySpriteClass();
	}

	@Source("images.css")
	OpusImagesCssResource css();
	
	@Source("projectdefaulticon.png")
	ImageResource projectdefaulticon();
	
	@Source("projectdefaulticon.png")
	DataResource projectdefaulticon2();
	
	@Source("loadingSpinner.gif")
	ImageResource loadingSpinner();
}
