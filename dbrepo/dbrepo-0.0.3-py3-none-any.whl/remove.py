import dbrepo as dbr

client = dbr.Client(username='jtaha',password='pw',url='http://s125.dl.hpc.tuwien.ac.at')
data = client.query_by_statement(1,1,"SELECT `time`,`stationid`,`compname` FROM `austria`")
print(data.time)