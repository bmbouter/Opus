package opus.community.gwt.management.console.client;

public class JSVariableHandler {

	public JSVariableHandler(){}
	
	public native String getRepoBaseURL()/*-{
		return $wnd.repoBaseURL;
	}-*/;

	public native String getDeployerBaseURL()/*-{
		return $wnd.deployerBaseURL;
	}-*/;
	
	public native String getCommunityBaseURL()/*-{
		return $wnd.communityBaseURL;
	}-*/;

}
