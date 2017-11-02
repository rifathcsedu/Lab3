'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import queue
import threading
import math
import random
import textwrap
from math import ceil


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 2
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def packetSegment(self, data_S, MTU):
        #print("I am a fool %s" %data_S)
        length=len(data_S)
        #print(length)
        #print((MTU-20))
        y=MTU-20
        packet=math.ceil(length/(MTU-20))
        #print(packet)
        packetData=[]
        if(data_S[0]!='0' and data_S[0]!='#'):
            ID=random.randint(100, 200)
            prev=-1    
            x=0
            lines = [data_S[i: i + y] for i in range(0, len(data_S), y)]
            i=0
            while i<len(lines):
                if (i==len(lines)-1):
                    st="#"+str(ID)+"#"+str(x)+"#0#"+str(prev)+"#"+lines[i]  
                else:
                    st="#"+str(ID)+"#"+str(x)+"#0#"+str(prev)+"#"+lines[i]
                packetData.append(st)
                prev=x
                x+=len(lines[i])
            
                #print(st)
                #print(len(st))
                #print(len(lines[i]))
                i+=1
        else:
            info=str(data_S).split("#")
            add=info[0]
            dst=info[1]
            ID=int(info[2])
            x=int(info[3])
            prev=int(info[5])
            data_S=info[6]
            #print(ID)
            lines = [data_S[i: i + y] for i in range(0, len(data_S), y)]
            #packetData=[]
        
            i=0
            while i<len(lines):
                if (i==len(lines)-1):
                    st=add+"#"+dst+"#"+str(ID)+"#"+str(x)+"#0#"+str(prev)+"#"+lines[i]  
                else:
                    st=add+"#"+dst+"#"+str(ID)+"#"+str(x)+"#0#"+str(prev)+"#"+lines[i]
                packetData.append(st)
                prev=x
                x+=len(lines[i])
            
                #print(st)
                #print(len(st))
                #print(len(lines[i]))
                i+=1
        return packetData
    def messageJoin(msg):
        st=""
        temp=-1
        min=100000000
        while len(msg)>0:
            i=0
            while i<len(msg):
                #print(self.msg[i].offset)
                if(msg[i].offset<min):
                    min=msg[i].offset
                    temp=i
                i+=1
            #print("Temp: %d"%temp)
            #print("Min: %d"%min)
            st+=msg[temp].message
            msg.pop(temp)
        return st    
    def __init__(self, dst_addr, data_S):
        self.dst_addr = dst_addr
        self.data_S = data_S
        
    ## called when printing the object
       
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self,addr):
        byte_S=str(addr).zfill(self.dst_addr_S_length)
        byte_S += "#"+str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]
        return self(dst_addr, data_S)
    

    
class message:
    def __init__(self,source,dest,id,offset,flag,prev,MS):
        self.ID=id
        self.dest=dest
        self.offset=offset
        self.flag=flag
        self.message=MS
        self.prev=prev
        self.source=source
## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
        finalMessage=""
        self.msg=[]
        
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
    
           
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        print("--------------Host %d sending-----------" %self.addr)
        data=NetworkPacket.packetSegment(self, data_S,self.out_intf_L[0].mtu)
        for i in data:
            p = NetworkPacket(dst_addr, i)
            self.out_intf_L[0].put(p.to_byte_S(self.addr)) #send packets always enqueued successfully
            print('%s: sending packet "%s" out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        info=str(pkt_S).split("#")
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, str(pkt_S)))
            print("-----------Print-----------")
            self.msg.append(message(int(info[0]),int(info[1]),int(info[2]),int(info[3]),int(info[4]),int(info[5]),info[6]))
            
    ## thread target for the host to keep receiving data
    
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                print("Message Length %d \n"%len(self.msg))
                if(len(self.msg)>0):
                    m=NetworkPacket.messageJoin(self.msg)
                    print("\n\nFinal message Host- %d got:\n%s\n\n\n" %(self.addr,m))
                return
        


## Implements a multi-interface router described in class
class Router:
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size,routingTable):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.msg=[]
        self.RoutingTable=routingTable
    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        #print(self.RoutingTable['2'][0])
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #info=str(pkt_S).split(",")
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    print("\n\n\n-----------Router-----------")
                    #self.msg.append(message(int(info[0]),int(info[1]),int(info[2]),int(info[3]),info[4]))
                    #p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    data=NetworkPacket.packetSegment(self, pkt_S,self.out_intf_L[i].mtu)
                    for j in data:
                        #p1 = NetworkPacket(dst_addr, j)
                        info=str(j).split("#")
                        if(self.name=='A'):
                            k=0
                            while k<len(self.RoutingTable['2']):
                                info1=str(self.RoutingTable['2'][k]).split(":")
                                if(int(info1[0])==int(info[0])):
                                    self.out_intf_L[int(info1[1])].put(j)
                                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, j, int(info1[1]), int(info1[1]), self.out_intf_L[int(info1[1])].mtu))
                                    break
                                k+=1
                        else:
                            k=0
                            while k<len(self.RoutingTable['2']):
                                info1=str(self.RoutingTable['2'][k]).split(":")
                                print(info1[0])
                                if(int(info1[0])==int(info[1])):
                                    self.out_intf_L[int(info1[1])].put(j)
                                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, j, int(info1[1]), int(info1[1]), self.out_intf_L[int(info1[1])].mtu))
                                    break
                                k+=1
                                                          
                         #send packets always enqueued successfully
        
                    #self.out_intf_L[i].put(p.to_byte_S(), True)
                        
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 