package opus.community.gwt.management.console.client.dashboard;

import opus.community.gwt.management.console.client.ServerCommunicator;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class DeleteProject extends Composite {

	private static DeleteProjectUiBinder uiBinder = GWT
			.create(DeleteProjectUiBinder.class);

	interface DeleteProjectUiBinder extends UiBinder<Widget, DeleteProject> {
	}

	private ServerCommunicator ServerComm; 
	private String projectTitle;
	
	@UiField Button deleteProjectButton;
	
	public DeleteProject(ServerCommunicator ServerComm, String projectTitle) {
		initWidget(uiBinder.createAndBindUi(this));
		this.ServerComm = ServerComm;
		this.projectTitle = projectTitle;
	}
	
	@UiHandler("deleteProjectButton")
	public void handleDeleteProjectButton(ClickEvent event){
		String postData = "";
		String url = "https://opus-dev.cnl.ncsu.edu:9007/deployments/" + projectTitle + "/destroy";
		ServerComm.doPost(url, postData);
		Window.alert("Posted");
	}
}
