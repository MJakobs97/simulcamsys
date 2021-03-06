from dataRep import DataRep
import asyncio
import functools


def compare_and_remove(dbdata, client_address_order, client_address_read_index, database) -> DataRep: 
 if not dbdata.id:
  dbdata.store(database)
 dbdata = DataRep.load(database, dbdata.id)
    
 if dbdata.data:
  #print("Dbdata.data in compare: \n",dbdata.data)
  for i in range(len(dbdata.data)): 
   #print("Looking for: \n", client_address_order[client_address_read_index])
   if str(client_address_order[client_address_read_index]) == dbdata.data[i].address:
    dbdata.data.remove(dbdata.data[i])
    #print("Removed: \n", str(dbdata.data[i]))
    return dbdata
       
def upload_data(clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database) -> int:
  for t in clients:
   if t.address == client_address_order[client_address_read_index] and t.services.characteristics[handle].uuid == QUERY_RSP_UUID:
    dbdata.data.append(address = t.address, battery = response.data[70][0], disk = int.from_bytes(response.data[54], "big"), gps= response.data[68][0])
    dbdata.store(database)
    if client_address_read_index < (len(client_address_order)-1):
     client_address_read_index = client_address_read_index +1
    else:
     client_address_read_index = 0
    return client_address_read_index

async def run_compare_threaded(dbdata, client_address_order, client_address_read_index, database) -> DataRep:
 try:
  if type(client_address_read_index) == int: 
   #print("Running compare threaded with this data: \n", str(client_address_order), client_address_read_index)
   dbdata_modified = await asyncio.get_event_loop().run_in_executor(None, functools.partial(compare_and_remove, dbdata, client_address_order, client_address_read_index, database))
   return dbdata_modified
  else:
   print("Client_address_read_index != int, aborting compare_and_remove()\n") 
 except Exception as ex: 
  print("Exception in run_compare_threaded: \n", ex)
  print("Current read index: \n", client_address_read_index)  

async def run_upload_threaded(clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database) -> int:
 try:
  if type(client_address_read_index) == int: 
   #print("Running upload threaded with this data: \n", str(client_address_order), client_address_read_index, str(dbdata))
   index = await asyncio.get_event_loop().run_in_executor(None, functools.partial(upload_data,clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database))
   print("Read_index after upload: \n", index)
  else:
   print("Client_address_read_index != int, aborting upload()\n")

  return index
 except Exception as ex: 
  print("Exception in run_upload_threaded: \n", ex)