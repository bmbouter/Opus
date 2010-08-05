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


class ModelProperties extends JavaScriptObject {                              // [1]
  // Overlay types always have protected, zero argument constructors.
  protected ModelProperties() {}                                              // [2]

  // JSNI methods to get stock data.
  public final native JavaScriptObject getFields() /*-{ return this.fields; }-*/; // [3]
 
} 
