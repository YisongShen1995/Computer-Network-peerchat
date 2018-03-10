#!/usr/bin/env python

"""
EE450 Homework 2 Client - STUB
Dr. Genevieve Bartlett
Fall 2017
"""

# You are not required to use any of the code in this stub,
# however you may find it a helpful starting point.
from collections import deque
import time
import socket
import sys
import select
import re

# In general, globals should be sparingly used if at all.
# However, for this simple program it's *ok*.
# You are not required to use these, but you may find them helpful.
our_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_input = deque()
network_input = deque()
network_output = deque()
network_address = deque()
network_addr = deque()
# You can keep your code simple by keeping a state transition table as a
# python dictionary (dictionary of lists or dictionary of dictionaries for
# example).  Again, for this simple program, you can make this a global
# variable.
block = False
local_ip = 0
local_mnum = 100
peer_list=['']
server_address = ('steel.isi.edu', 63682)
msg_to_send= ''
msg=''
timer1 = 0
current_time = 0
timer2 = 0
sleep = 0
recieve_ack=False
key=True
msg_to_send=''
msg_address=''
now = 0
sleep = 0
def register():
    global our_socket,server_address,msg_to_send,local_mnum,local_ip
    data_mnum = local_mnum
    data_src='{0:03d}'.format(0)
    data_dst='{0:03d}'.format(999)
    data_pnum=1
    data_hct=1
    data_msg='register'
    src=['SRC:',str(data_src),';DST:',str(data_dst),';PNUM:',str(data_pnum),';HCT:',str(data_hct),';MNUM:',str(data_mnum),';VL:;','MESG:',str(data_msg)]
    msg_to_send = str("".join(src))
    our_socket.sendto(msg_to_send.encode('utf-8'), server_address)
    local_mnum = local_mnum+1
    data,addr = our_socket.recvfrom(1024)
    x= data.split(';')
    local_ip=x[1].split(':')[1]
    if local_ip!='000':
        print('Successfully registered. My ID is: %s'% local_ip )
    else:
        print('%s' %x[6])
    

def handle_io():
    global our_socket, local_input, network_input, network_output,network_address,block
    global server_address, msg_to_send, local_ip, local_mnum, addr,peer_list,key,timer1,current_time,timer2,recieve_ack,msg_to_send,msg_address,now,sleep,network_addr
    #auto keep id alive every 45 seconds
    if now>0:
        sleep=sleep+time.time()-now
    now=time.time()
    if sleep>45:
        print('Automatically get current map')
        local_input.append('ids')
        sleep=0
    try:
        msg_from_server = network_input.pop()
        addr=network_addr.pop()
        src=msg_from_server.split(';')
        data_pnum = src[2].split(':')[1]
        data_msg = src[6].split(':')[1]
        recieve_hct=int(src[3].split(':')[1])
        recieve_src=src[1].split(':')[1]
        recieve_dst=src[0].split(':')[1]
        recieve_mnum=src[4].split(':')[1]
        recieve_vl=src[5].split(':')[1].split(',')
        recieve_msg=data_msg
        recieve_pnum=data_pnum
        # ids,get peer and save in list and print oout
        if data_pnum=='6':
            print("*********************")
            print("Recently Seen Peers:")
            src=data_msg.split('a')[0].split('=')
            output=src[1].split(',')
            output.remove(local_ip)
            print ','.join(output)
            print('')
            print('Known addresses:')
            src2 = data_msg.split('d')[2].split(',')
            peer_list=src2
            for ip in src2:
                if ip.split('=')[0]!=local_ip:
                    print(ip.split('=')[0]+' '+ip.split('=')[1].split('@')[0]+' '+ip.split('=')[1].split('@')[1])
            print("*********************")
        # recieve message and send ack back. if dst is local ip, fine. if not forwarding
	elif data_pnum == '3':
            print("*********************")
            data_dst=src[0].split(':')[1]
            print ('Recieve message: "%s" from %s' %(data_msg,data_dst))
            data_msg = 'ACK'
	    data_src=src[1].split(':')[1]
            data_dst=src[0].split(':')[1]
            data_mnum=src[4].split(':')[1]
            data_hct=1
            data_pnum=4
        # local ip (send to my ip)
            if data_src==local_ip:
                src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:;', 'MESG:', data_msg]
                network_output.append(str(''.join(src)))
                network_address.append(addr)
        # forwarding
            else:
                src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:;', 'MESG:', data_msg]
                network_output.append(str(''.join(src)))
                network_address.append(addr)
        # check hct value
                print('Message "%s" is a forwarding message from %s'%(msg_from_server,data_dst))
                if recieve_hct==0:
                    print('*****************')
                    print('Dropper message from %s to %s - hop count exceeded' %(recieve_dst,recieve_src))
                    print('MESG: %s' %recieve_msg)
                elif recieve_hct>0:
                    test = False
                    data_hct=recieve_hct-1
                    for ip in recieve_vl:
                        if local_ip==ip:
                            test=True
        # peer revisited
                    if test:
                        print('*****************')
                        print('Dropper message from %s to %s - peer revisited' %(recieve_dst,recieve_src))
                        print('MESG: %s' %recieve_msg)
        # keep forwarding
                    else:   
                        print('Forwarding')
                        recieve_vl.append(local_ip)
                        data_vl=str(','.join(recieve_vl))
        # set a block, add all peer ip but local to network output. If one message successfully forwarding, block other(to make sure less than 3 node get, i choose to send to one node per forwarding)
                        block=False
                        for ip in peer_list:
                            if local_ip!=ip.split('=')[0]:
                                src = ['SRC:', str(recieve_dst), ';DST:', str(recieve_src), ';PNUM:', str(recieve_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:',data_vl,';', 'MESG:', recieve_msg]
                                network_output.appendleft(str(''.join(src)))
                                hostname=ip.split('=')[1].split('@')[0]
                                port=int(ip.split('=')[1].split('@')[1])
                                address=(hostname,port)
                                network_address.appendleft(address)
        #Deal with ack feedback. Check if it is forwarding by vl list. If it is forwarding ack,set block true. Key is used to make sure send message for five times.                         
        elif data_pnum == '4':
            src=msg_to_send.split(';')
            sr=src[1].split(':')[1]
            dst=src[0].split(':')[1]
            mnum=src[4].split(':')[1]
            if recieve_src==dst and recieve_dst==sr and mnum==recieve_mnum:
               recieve_ack= True
               key=True
               print('******************')
               print('Recieve ACK')
               print('******************')
               if src[5].split(':')[1]!='':
                   block = True
                   print('Successfully forwarding')
                   print('******************')
        elif data_pnum== '8':
            src=msg_to_send.split(';')
            sr=src[1].split(':')[1]
            dst=src[0].split(':')[1]
            mnum=src[4].split(':')[1]
            if recieve_src==dst and recieve_dst==sr and mnum==recieve_mnum:
               recieve_ack= True
               key=True
               print('******************')
               print('Recieve ACK')
               print('******************')
         #Broadcasting
        elif data_pnum == '7':
            print("*********************")
            print('SRC: %s broadcasted:'%src[0].split(':')[1])
            print('MESG: %s' %data_msg)
            print("*********************")
            data_msg = 'ACK'
	    data_src=src[1].split(':')[1]
            data_dst=src[0].split(':')[1]
            data_mnum=src[4].split(':')[1]
            data_hct=1
            data_pnum=8
            src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:;', 'MESG:', data_msg]
            network_output.append(str(''.join(src)))
            network_address.append(addr)
        return
    except IndexError:
        # use indexerror to handle resend
        # for ack, get map, register send only one time so pass
        # if recieve_ack is true which means recieve ack, pass
        # if no message in output pass
        if msg_to_send!='' and msg_to_send.split(';')[6].split(':')[1]=='ACK':
            key=True
            recieve_ack=True
            timer2 = 0
            timer1 = 0
            current_time=0
            pass
        elif msg_to_send!='' and msg_to_send.split(';')[6].split(':')[1]=='get map':
            key=True
            recieve_ack=True
            timer2 = 0
            timer1 = 0
            current_time=0
            pass
        elif recieve_ack:
            key=True
            timer2 = 0
            timer1 = 0
            current_time=0
            pass
        elif msg_to_send=='' and len(network_output)==0:
            key=True
            timer2 = 0
            timer1 = 0
            current_time=0
            pass
        elif msg_to_send!='' and msg_to_send.split(';')[6].split(':')[1]=='register':
            key=True
            recieve_ack=True
            timer2 = 0
            timer1 = 0
            current_time=0
            pass
        #else you need to check. Every time after send message, we set key=false to block the network_output. We set select time out as 1 seconds. Here we use two timer, timer1 is larger than 1 second(select timeout) which means we wait 1 second and get no ack, set key=true to unblock the output, reset timer1 and resend the message. If timer2 is larger than 5 seconds which means we wait for five times and get no ack. So reset timer2 and gave error message. If recieve ack, it will go to previous case and pass.
        else:
            if current_time>0 :
                timer1 = timer1 +time.time()-current_time
                timer2 = timer2 +time.time()-current_time
            current_time=time.time()

            if timer2>5:
                timer2 = 0
                timer1 = 0
                current_time=0
                if msg_to_send.split(';')[5].split(':')[1]=='':
                    print('******************')
                    print('ERROR: Gave up sending to %s' %msg_to_send.split(';')[1].split(':')[1])
                    print('******************')
                    key=True
                    msg_to_send=''
                else:
                    print('******************')
                    print('ERROR: Gave up forwarding with this address')
                    print('******************')
                    key=True
                    msg_to_send=''
            else:
                if timer1>1:
                    timer1=0
                    key=True
                    network_output.append(msg_to_send)
                    network_address.append(msg_address)
            return
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise
    if len(network_output)>0:
        return
    try:
        # use lower to deal with lower case and upper case
        input1 = local_input.pop()
        if input1.lower()== 'ids':
            data_msg = 'get map'
            data_pnum = 5
	    data_src=local_ip
            data_dst='{0:03d}'.format(999)
            data_mnum=local_mnum
            data_hct=1
            src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:','',';', 'MESG:', data_msg]
            network_output.appendleft(str(''.join(src)))
            network_address.appendleft(server_address)
        # msg
        elif input1.lower().split(' ')[0]=='msg':
	    data_dst=input1.lower().split(' ')[1]
            data_msg=' '.join(input1.split(' ')[2:])
            data_pnum = 3
	    data_src=local_ip
            data_mnum=local_mnum
            data_hct=1
            test = False
            for ip in peer_list:
                if ip.split('=')[0]==data_dst:
                    hostname=ip.split('=')[1].split('@')[0]
                    port=int(ip.split('=')[1].split('@')[1])
                    address=(hostname,port)
                    test = True
            if test:
                src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:','',';', 'MESG:', data_msg]
                msg=str(''.join(src))
                network_output.appendleft(msg)
                network_address.appendleft(address)
        # forwarding
            else:
                print('******************')
                print('Not a peer node, forwarding')
                print('******************')
                block=False
                data_hct=9
                recieve_vl=[local_ip]
                data_vl=str(' '.join(recieve_vl))
                count=0
                for ip in peer_list:
                    if local_ip!=ip.split('=')[0]:
                        src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:',data_vl,';', 'MESG:', data_msg]
                        network_output.appendleft(str(''.join(src)))
                        hostname=ip.split('=')[1].split('@')[0]
                        port=int(ip.split('=')[1].split('@')[1])
                        address=(hostname,port)
                        network_address.appendleft(address)
        #broadcasting                
        elif input1.lower().split(' ')[0]=='all':
            data_msg=' '.join(input1.split(' ')[1:])
            data_pnum = 7
	    data_src=local_ip
            data_mnum=local_mnum
            data_hct=1
            for ip in peer_list:
                if ip.split('=')[0]!=local_ip:
                    hostname=ip.split('=')[1].split('@')[0]
                    port=int(ip.split('=')[1].split('@')[1])
                    address=(hostname,port)
                    data_dst=ip.split('=')[0]
                    src = ['SRC:', str(data_src), ';DST:', str(data_dst), ';PNUM:', str(data_pnum), ';HCT:', str(data_hct), ';MNUM:', str(data_mnum), ';VL:;', 'MESG:', data_msg]
                    msg=str(''.join(src))
                    network_output.appendleft(msg)
                    network_address.appendleft(address)
        #after send every message, increase mnum
        local_mnum=local_mnum+1
        return
    except IndexError:
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise
    return
def run_loop():
    global our_socket, local_input, network_input, network_output,server_address,addr,local_mnum,key,recieve_ack,msg_to_send,msg_address,block,network_addr
    watch_for_read = [sys.stdin, our_socket]
    while True:
        try:
            #set key to block and wait for ack
            if len(network_output) > 0 and key:
                watch_for_write = [our_socket]
            else:
                watch_for_write = []
            input_ready, output_ready, except_ready = select.select(watch_for_read, watch_for_write, watch_for_read, 1)

            for item in input_ready:
                if item == sys.stdin:
                    data = sys.stdin.readline().strip()
                    if len(data) > 0:
                        local_input.appendleft(str(data))
                    else:
                        pass
                if item == our_socket:
                    data,addr = our_socket.recvfrom(1024)
                    if len(data) > 0:
                        network_input.appendleft(str(data))
                        network_addr.appendleft(addr)
                    else:
                        our_socket.close()
                        return
            for item in output_ready:
                if item == our_socket:
                    try:
            #set block to filt forwarding make sure forwarding send to at most one address
                        while block:
                            if network_output[len(network_output)-1].split(';')[5].split(':')[1]!='':
                                network_output.pop()
                                network_address.pop()
                            else: 
                                break
                        msg_to_send = network_output.pop()
                        msg_address = network_address.pop()
                        print ('Sending message "%s" to address "%s"'%(msg_to_send,msg_address))
                        our_socket.sendto(msg_to_send,msg_address)
            #set key block and wait for ack
                        key=False
                        recieve_ack=False
                    except IndexError:
                        pass
                    except Exception as e:
                        print("Unhandled send exception: %s" % e)

            for item in except_ready:
                if item == our_socket:
                    our_socket.close()
                    return
        except KeyboardInterrupt:
            our_socket.close()
            return
        except Exception as e:
            print("Unhandled exception 0: %s" % e)
            return
    	handle_io()
if __name__ == "__main__":
    register()
    run_loop()


