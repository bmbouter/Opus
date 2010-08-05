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

import opus.gwt.management.console.client.JSVariableHandler;
import opus.gwt.management.console.client.resources.ProjectURLPopupCss.ProjectURLPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class AddProjectFromURL extends Composite {

	private static AddProjectFromURLUiBinder uiBinder = GWT
			.create(AddProjectFromURLUiBinder.class);

	interface AddProjectFromURLUiBinder extends
			UiBinder<Widget, AddProjectFromURL> {
	}
	
	private final String projConfigURL = "/project/configuration/token/";
	
	private AddAppsBuildProject appBuilder;
	private JSVariableHandler JSVarHandler;
	
	@UiField ProjectURLPopupStyle style;
	@UiField Button addProjectFromURLButton;
	@UiField PopupPanel addProjectFromURLPopup;
	@UiField TextBox projectTokenTextBox;
	
	public AddProjectFromURL(AddAppsBuildProject appBuilder) {
		initWidget(uiBinder.createAndBindUi(this));	
		//AddProjectFromURLUiBinder uiBinder = GWT.create(AddProjectFromURLUiBinder.class);
	    //uiBinder.createAndBindUi(this);
		JSVarHandler = new JSVariableHandler();
	    addProjectFromURLPopup.setAutoHideEnabled(true);
	    addProjectFromURLPopup.hide();
	    addProjectFromURLPopup.setGlassEnabled(true);
	    addProjectFromURLPopup.setGlassStyleName(style.applicationPopupGlass());
	    addProjectFromURLPopup.addCloseHandler(new CloseHandler<PopupPanel>(){
	    	@Override
	    	public void onClose(CloseEvent<PopupPanel> event) {
	    		projectTokenTextBox.setText("");
	    	}
	    });
	    this.appBuilder = appBuilder;
	}
	
	public void show() {
		addProjectFromURLPopup.center();
		addProjectFromURLPopup.show();
	}

	public void hide() {
		addProjectFromURLPopup.hide();
	}

	@UiHandler("addProjectFromURLButton")
	void onClick(ClickEvent e) {
		appBuilder.addProject(URL.encode(JSVarHandler.getRepoBaseURL() + projConfigURL.replaceAll("token", projectTokenTextBox.getText())));
    	this.hide();
	  
	}
}
