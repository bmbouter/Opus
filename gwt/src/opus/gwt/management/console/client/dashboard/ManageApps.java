package opus.gwt.management.console.client.dashboard;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class ManageApps extends Composite {

	private static EditAppsUiBinder uiBinder = GWT
			.create(EditAppsUiBinder.class);

	interface EditAppsUiBinder extends UiBinder<Widget, ManageApps> {
	}

	public ManageApps() {
		initWidget(uiBinder.createAndBindUi(this));
	}
}
