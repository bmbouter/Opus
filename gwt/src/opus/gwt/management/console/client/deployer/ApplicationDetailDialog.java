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

import opus.gwt.management.console.client.resources.ApplicationPopupCss.ApplicationPopupStyle;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

public class ApplicationDetailDialog extends Composite {

	private static ApplicationDetailInformationUiBinder uiBinder = GWT
			.create(ApplicationDetailInformationUiBinder.class);

	interface ApplicationDetailInformationUiBinder extends
			UiBinder<Widget, ApplicationDetailDialog> {
	}


	 @UiField PopupPanel applicationPopup;
	 @UiField FlexTable versionsFlexTable;
	 @UiField ApplicationPopupStyle style;
	  
	 
	  public ApplicationDetailDialog() {
		ApplicationDetailInformationUiBinder uiBinder = GWT.create(ApplicationDetailInformationUiBinder.class);
	    uiBinder.createAndBindUi(this);
	    applicationPopup.setAutoHideEnabled(true);
	    applicationPopup.hide();
	    applicationPopup.setGlassEnabled(true);
	    applicationPopup.setGlassStyleName(style.applicationPopupGlass());
	  }

	  public void show() {
		 applicationPopup.center();
		 applicationPopup.show();
	  }

	  public void hide() {
		  applicationPopup.hide();
	  }
}
