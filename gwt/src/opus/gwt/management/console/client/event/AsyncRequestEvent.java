package opus.gwt.management.console.client.event;

import com.google.gwt.event.shared.GwtEvent;


public class AsyncRequestEvent extends GwtEvent<AsyncRequestEventHandler> {
	
	public static Type<AsyncRequestEventHandler> TYPE = new Type<AsyncRequestEventHandler>();
	private String requestHandle;
	private String urlVariable;
	private boolean hasUrlVariable;
	
	public AsyncRequestEvent(String requestHandle){
		this.requestHandle = requestHandle;
		this.hasUrlVariable = false;
	}
	
	public AsyncRequestEvent(String requestHandle, String urlVariable){
		this.requestHandle = requestHandle;
		this.urlVariable = urlVariable;
		this.hasUrlVariable = true;
	}
	
	public String getRequestHandle(){
		return requestHandle;
	}
	
	public String getUrlVariable(){
		return urlVariable;
	}
	
	public boolean hasUrlVariable(){
		return hasUrlVariable;
	}
	
  	@Override
  	public Type<AsyncRequestEventHandler> getAssociatedType() {
	  return TYPE;
  	}

  	@Override
  	protected void dispatch(AsyncRequestEventHandler handler) {
	  handler.onAsyncRequest(this);
  	}
}