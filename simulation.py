'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network
import link
import threading
import textwrap
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 3 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    client1 = network.Host(1)
    object_L.append(client1)
    server1 = network.Host(3)
    object_L.append(server1)
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    link_layer.add_link(link.Link(client1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(router_a, 0, server1, 0, 30))
    
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client1.__str__(), target=client1.run))
    thread_L.append(threading.Thread(name=server1.__str__(), target=server1.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
    str='I am expecting a lot of transfer activity from last season top six.(give the network).give the network sufficient time to transfer all packets before quitting'
    #create some send events
    #print(len(str))
    client1.udt_send(3, str)
    
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically