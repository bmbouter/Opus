package opus.gwt.management.console.client.appbrowser;

public class JSVariableHandler {

	public JSVariableHandler(){}
	
	public native String getRepoBaseURL()/*-{
		return $wnd.repoBaseURL;
	}-*/;

	public native String getBuildProjectURL()/*-{
		return $wnd.buildProjectURL;
	}-*/;

	
	public native String getDeployerBaseURL()/*-{
		return $wnd.deployerBaseURL;
	}-*/;
	
	public native String getProjectToken()/*-{
		return $wnd.projectToken;
	}-*/;
}
