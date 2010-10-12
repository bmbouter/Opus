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

package opus.gwt.management.console.client.deployer;

import opus.gwt.management.console.client.event.PanelTransitionEvent;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.Widget;

public class ConfirmProject extends Composite {

	private static ConfirmBuildProjectUiBinder uiBinder = GWT
			.create(ConfirmBuildProjectUiBinder.class);

	interface ConfirmBuildProjectUiBinder extends
			UiBinder<Widget, ConfirmProject> {
	}

	private FormPanel deployerForm;
	private ProjectDeployerController projectDeployerController;
	private HandlerManager eventBus;
	
	@UiField ScrollPanel confirmationScrollPanel;
	@UiField Button previousButton;
	
	public ConfirmProject(FormPanel deployerForm, HandlerManager eventBus) {
		initWidget(uiBinder.createAndBindUi(this));
		this.deployerForm = deployerForm;
		this.projectDeployerController = projectDeployerController;
	}
	
	@UiHandler("previousButton")
	void handlePreviousButton(ClickEvent event){
		eventBus.fireEvent(new PanelTransitionEvent(PanelTransitionEvent.TransitionTypes.PREVIOUS, this));
	}
	
	@UiHandler("confirmButton")
	void handleConfirmButton(ClickEvent event){
		projectDeployerController.handleConfirmDeployProject();
	}
}
