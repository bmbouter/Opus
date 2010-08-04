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
import opus.gwt.management.console.client.ServerCommunicator;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.http.client.URL;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class Dashboard extends Composite {

	private static DashboardUiBinder uiBinder = GWT
			.create(DashboardUiBinder.class);

	interface DashboardUiBinder extends UiBinder<Widget, Dashboard> {
	}

	private final String projectInfoURL = "/json/projectName/?a&callback=";
	
	private ServerCommunicator serverComm;
	private JSVariableHandler JSVarHandler;

	@UiField FlowPanel applicationsFlowPanel;
	@UiField Label dbnameLabel;
	@UiField Label dbengineLabel;
	@UiField Label activeLabel;
	@UiField FlowPanel urlsFlowPanel;
	
	public Dashboard(String projectName, ServerCommunicator serverComm) {
		initWidget(uiBinder.createAndBindUi(this));
		this.serverComm = serverComm;
		JSVarHandler = new JSVariableHandler();
		getProjectInfo(projectName);
	}
	
	private void getProjectInfo(String projectName){
		final String url = URL.encode(JSVarHandler.getDeployerBaseURL() + projectInfoURL.replaceAll("/projectName/", "/" + projectName +"/"));
		serverComm.getJson(url, serverComm, "handleProjectInformation", this);
	}
	
	public void handleProjectInformation(ProjectInformation projInfo){
		dbnameLabel.setText(projInfo.getDBName());
		dbengineLabel.setText(projInfo.getDBEngine());
		if(projInfo.getActive()){
			activeLabel.setText("Yes");
		} else {
			activeLabel.setText("No");
		}
		for(int i =0; i < projInfo.getApps().length(); i++){
			int index = projInfo.getApps().get(i).indexOf(".");
			applicationsFlowPanel.add(new Label(projInfo.getApps().get(i).substring(index+1)));	
		}
		for(int i =0; i < projInfo.getURLS().length(); i++){
			urlsFlowPanel.add(new HTML("<a href='" + projInfo.getURLS().get(i) + "'>" + projInfo.getURLS().get(i) + "</a>"));	
		}
	}
	
	public final native ProjectInformation asJSOProjectInformation(JavaScriptObject jso) /*-{
		return jso;
	}-*/;
	
}
