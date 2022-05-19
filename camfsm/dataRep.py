from couchdb.mapping import Document, ListField, TextField, DictField, Mapping

class DataRep(Document):
 #data representation within couchdb, 1 "object" per client with MAC and actual data
 data = ListField(DictField(Mapping.build(address = TextField(), battery = TextField(), disk = TextField(), gps = TextField())))