package opus.gwt.management.console.client.deployer;

import opus.gwt.management.console.client.ClientFactory;
import opus.gwt.management.console.client.overlays.DjangoPackage;

import com.google.gwt.cell.client.CheckboxCell;
import com.google.gwt.cell.client.FieldUpdater;
import com.google.gwt.core.client.GWT;
import com.google.gwt.safehtml.shared.SafeHtmlUtils;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.cellview.client.CellTable;
import com.google.gwt.user.cellview.client.Column;
import com.google.gwt.user.cellview.client.SimplePager;
import com.google.gwt.user.cellview.client.TextColumn;
import com.google.gwt.user.cellview.client.SimplePager.TextLocation;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.view.client.ListDataProvider;
import com.google.gwt.view.client.MultiSelectionModel;
import com.google.gwt.view.client.ProvidesKey;

public class DPCellTable extends Composite {

	private static DPCellTableUiBinder uiBinder = GWT.create(DPCellTableUiBinder.class);
	interface DPCellTableUiBinder extends UiBinder<Widget, DPCellTable> {}

	private ClientFactory clientFactory;
	public final MultiSelectionModel<DjangoPackage> selectionModel;
	
	@UiField(provided = true) CellTable<DjangoPackage> cellTable;
	@UiField(provided = true) SimplePager pager;
	
	public DPCellTable(ClientFactory clientFactory) {
		this.clientFactory = clientFactory;
		ProvidesKey<DjangoPackage> keyProvider = new ProvidesKey<DjangoPackage>() {
		      public Object getKey(DjangoPackage item) {
		        return (item == null) ? null : item.getPk();
		      }
		};
		
		cellTable = new CellTable<DjangoPackage>(keyProvider);
	    
		// Create a Pager to control the table.
	    SimplePager.Resources pagerResources = GWT.create(SimplePager.Resources.class);
	    pager = new SimplePager(TextLocation.CENTER, pagerResources, false, 0, true);
	    pager.setDisplay(cellTable);
		
	    selectionModel = new MultiSelectionModel<DjangoPackage>(keyProvider);
	    cellTable.setSelectionModel(selectionModel);
	    
	    initTableColumns(selectionModel);
	    
		initWidget(uiBinder.createAndBindUi(this));
	}

	private void initTableColumns(final MultiSelectionModel<DjangoPackage> selectionModel){
		Column<DjangoPackage, Boolean> checkColumn = new Column<DjangoPackage, Boolean>(new CheckboxCell(true)) {
			@Override
			public Boolean getValue(DjangoPackage object) {
				// Get the value from the selection model.
				return selectionModel.isSelected(object);
			}
		};
		checkColumn.setFieldUpdater(new FieldUpdater<DjangoPackage, Boolean>() {
		  public void update(int index, DjangoPackage object, Boolean value) {
		    // Called when the user clicks on a checkbox.
		    selectionModel.setSelected(object, value);
		  }
		});
		cellTable.addColumn(checkColumn, SafeHtmlUtils.fromSafeConstant("<br>"));
	    
		TextColumn<DjangoPackage> nameColumn = new TextColumn<DjangoPackage>(){
			@Override
			public String getValue(DjangoPackage djangoPackage){
				return djangoPackage.getAppName();
			}
		};
		
		TextColumn<DjangoPackage> descriptionColumn = new TextColumn<DjangoPackage>(){
			@Override
			public String getValue(DjangoPackage djangoPackage){
				return djangoPackage.getDescription();
			}
		};
		
		cellTable.addColumn(nameColumn, "App Name");
		cellTable.addColumn(descriptionColumn, "Description");
		cellTable.setRowCount(clientFactory.getDjangoPackages().size(), true);
		ListDataProvider<DjangoPackage> dataProvider = new ListDataProvider<DjangoPackage>(clientFactory.getDjangoPackages());
		dataProvider.addDataDisplay(cellTable);
	}
	
}
