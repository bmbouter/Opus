package opus.community.gwt.management.console.client.dashboard;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
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
