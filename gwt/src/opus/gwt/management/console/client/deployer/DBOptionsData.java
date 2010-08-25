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

import com.google.gwt.core.client.JavaScriptObject;

public class DBOptionsData extends JavaScriptObject {
	protected DBOptionsData() {}                                 

	public final native boolean getAutoPostgresConfig() /*-{ 
		return this.OPUS_AUTO_POSTGRES_CONFIG; 
	}-*/;
	public final native String getAllowedDatabases() /*-{
		var allowed = "";
		for(var i = 0; i < this.OPUS_ALLOWED_DATABASES.length; i++){
			allowed += this.OPUS_ALLOWED_DATABASES[i] + ",";
		} 
		allowed = "sqlite3,mysql,postgresql_psycopg2";
		return allowed; 
	}-*/;
	 
}
