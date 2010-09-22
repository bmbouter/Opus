/*############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
############################################################################*/

package opus.gwt.management.console.client.dashboard;

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.PanelManager;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;

public class DeleteProject extends Composite {

	private static DeleteProjectUiBinder uiBinder = GWT
			.create(DeleteProjectUiBinder.class);

	interface DeleteProjectUiBinder extends UiBinder<Widget, DeleteProject> {
	}

	private final String deleteProjectURL = "/deployments/projectName/destroy";
	
	private JSVariableHandler JSVarHandler;
	private FormPanel deleteForm;
	private ProjectManager projectManager;
	private String projectName;
	
	@UiField Button deleteProjectButton;
	@UiField HTMLPanel mainDeleteProjectPanel;
	@UiField FlowPanel titlePanel;
	
	public DeleteProject(ProjectManager projectManager) {
		initWidget(uiBinder.createAndBindUi(this));
		this.projectManager = projectManager;
		JSVarHandler = new JSVariableHandler();
		deleteForm = new FormPanel();
		projectName = "";
	}
	
	private void setupDeleteForm(){
		deleteForm.setMethod(FormPanel.METHOD_POST);
		deleteForm.setVisible(false);
		deleteForm.setAction(JSVarHandler.getDeployerBaseURL() + deleteProjectURL.replaceAll("/projectTitle/", "/" + projectName +"/"));
		titlePanel.add(deleteForm);
		final String deletedProject = projectName;
		deleteForm.addSubmitHandler(new FormPanel.SubmitHandler() {
		      public void onSubmit(SubmitEvent event) {
		        deleteForm.add(new Hidden("csrfmiddlewaretoken", Cookies.getCookie("csrftoken")));
		      }
		 });
		deleteForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
		      public void onSubmitComplete(SubmitCompleteEvent event) {
		        //managementCon.onProjectDelete(deletedProject);
		      }
		 });
	}
	
	@UiHandler("deleteProjectButton")
	public void handleDeleteProjectButton(ClickEvent event){
		deleteForm.submit();
	}
}