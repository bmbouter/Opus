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

package opus.gwt.management.console.client.resources;

import com.google.gwt.core.client.GWT;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.CssResource;

public interface ManagementConsoleControllerResources extends ClientBundle {
	public static final ManagementConsoleControllerResources INSTANCE = GWT.create(ManagementConsoleControllerResources.class);
	
	public interface ManagementConsoleControllerStyle extends CssResource {
	    String dashboardsPopup();
	    String popupLabel();
	    String popupLabelActive();
	    String topDashboardButtonActive();
	    String topDashboardButton();
	    String projectIcon();
	    String projectIconActive();
	    String lastLabel();
	    String rootLayoutPanel();
	}
}