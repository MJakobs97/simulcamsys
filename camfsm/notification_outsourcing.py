from dataRep import DataRep
import asyncio
import functools


def compare_and_remove(dbdata, client_address_order, client_address_read_index, database): 
 if not dbdata.id:
  dbdata.store(database)
 dbdata = DataRep.load(database, dbdata.id)
    
 if dbdata.data:
  print(dbdata.data)
  for i in range(len(dbdata.data)): 
   print("Looking for: \n", client_address_order[client_address_read_index])
   if str(client_address_order[client_address_read_index]) == dbdata.data[i].address:
    dbdata.data.remove(dbdata.data[i])
    #print("Removed: \n", str(dbdata.data[i]))
       
def upload_data(clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database):
  for t in clients:
   if t.address == client_address_order[client_address_read_index] and t.services.characteristics[handle].uuid == QUERY_RSP_UUID:
    dbdata.data.append(address = t.address, battery = response.data[70][0], disk = int.from_bytes(response.data[54], "big"), gps= response.data[68][0])
    dbdata.store(database)
    if client_address_read_index < (len(client_address_order)-1):
     client_address_read_index = client_address_read_index +1
    else:
     client_address_read_index = 0
    return client_address_read_index

async def run_compare_threaded(dbdata, client_address_order, client_address_read_index, database):
 try:
  print("Running compare threaded with this data: \n", str(dbdata), str(client_address_order), client_address_read_index, repr(database))

  await asyncio.get_event_loop().run_in_executor(None, functools.partial(compare_and_remove, dbdata, client_address_order, client_address_read_index, database))
 except Exception as ex: 
  print("Exception in run_compare_threaded: \n", ex)  

async def run_upload_threaded(clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database):
 try:
  print("Running upload threaded with this data: \n", repr(clients), str(client_address_order), client_address_read_index, handle, QUERY_RSP_UUID, str(dbdata), response, repr(database))
  await asyncio.get_event_loop().run_in_executor(None, functools.partial(upload_data,clients, client_address_order, client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database))
 except Exception as ex: 
  print("Exception in run_upload_threaded: \n", ex)