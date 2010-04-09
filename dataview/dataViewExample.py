import dataview_client as dvclient

'''
Properties are a dictionary where keys are property names and values can be either strings
or tuples in the form of ("type","value") where type is one of the Azure supported types:
      
Edm.Binary     Array of bytes up to 64 KB in size.
Edm.Boolean    Boolean value.
Edm.DateTime   64-bit value expressed as Coordinated Universal Time (UTC). 
Edm.Double     64-bit floating point value.
Edm.Guid       128-bit globally unique identifier.
Edm.Int32      32-bit integer.
Edm.Int64      64-bit integer.
Edm.String     UTF-16-encoded value. String values may be up to 64 KB in size.

Every entry must contain PartitionKey and RowKey. Both have to be strings.
'''
props = {"Double":("Edm.Double","33.33"),"Address": "Cary","PartitionKey":"p","RowKey":"4"}
client = dvclient.DVClient("https://opus-dev.cnl.ncsu.edu:9004","dennis")
test_table = "TestTable2"

print client.create_table(test_table)

print client.insert(test_table, props)

for k in client.get_all_from_table(test_table):
    print k.Address


#print dir(client.get_all_from_table(test_table))
