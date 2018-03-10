1 Overview
Your task is to complete a UDP peer-to-peer client which contacts a registration server to obtain
a peer ID. Your peer will also contact the registration server to download a list of available peers
you can contact. With this contact list you can send messages between peers.

1.1 Message Format
Messages in this protocol will have pairs of eld names and values. A eld name and its value
will be separated by a colon. In every message, these eld-name:value pairs will be separated by
a semicolon.
All messages will have the following format:
SRC:###;DST:###;PNUM:#;HCT:#;MNUM:###;VL:xxx;MESG:yyy
In the above format (and throughout this document), # denotes a digit (0-9). xxx may be
empty or may be a comma separated list of three digit numbers and yyy may be blank or a
series of up to 200 ASCII characters. yyy can be made up of any printable ASCII characters
except the following characters:
' " ; :
The elds in the message are as follows:
SRC denotes the three digit ID of the sender of the message and may have a value between 0
(000) and 999. 000 is a reserved ID, as is 999.
DST denotes the three digit ID of the intended recipient of a message and may have a value
between 0 (000) and 999. Again, 000 is a reserved ID, as is 999.
PNUM denotes the protocol message number and may have a value between 0 and 9. The
following is a list of what each protocol message number indicates:
PNUM value Description
1 Registration request
2 Registration response
3 Data
4 Data conrmation
5 Request for current peer registry
6 Current Peer Registry
7 Serial Broadcast
8 Serial Broadcast conrmation
0 Error message
HCT denotes the hop count|the remaining number of times a message may be forwarded on
and can be between 0 and 9. The HCT eld is only relevant for messages being forwarded
(discussed later).
MNUM a message ID number. Your client will generate these for every newly written message
originating at your client. The message ID will help you match requests and responses.
Even numbered PNUM messages are responses, and will have the same message ID as
the request which prompted the reply. For example, if you send data (PNUM:3) with a
message ID of 123, the data conrmation (PNUM:4) response should also have message
ID 123. Generate message IDs in order, starting with whatever number you wish|we
recommend starting with 100 so you already have a three digit value.
VL a comma separated list of three digit peer IDs which indicates which peers have already seen
a forwarded message. Like HCT, this value is only important for messages being forwarded
(discussed later).
MESG the message contents.

2 User Interface and Detailed Instructions
There are ve \steps" to completing this project. Each is described in detail in the following
subsections.
Upon starting, your program should:
1. Connect to the registration server at steel.isi.edu:63682, and register with the name server
(Step #1).
2. Then, run a loop which waits for keyboard input and understands the following commands:
ids as described in Step #2
msg ### <string> as described in Step #3.
all <string> as described in Step #4
Commands may be lower-case, upper-case or a mix of upper and lower case. Commands are
entered via typing and then pressing the <enter> key.
2.1 Step #1, Register
Send a message to the registration server at steel.isi.edu:63682, and register with the server. The
server will give you a numeric name consisting of three digits.
The message for a registration request should be:
SRC:000;DST:999;PNUM:1;HCT:1;MNUM:###;VL:;MESG:register
where ### denotes any three digit number you generate for a message ID.
2.2 Step #2, Pull Registry
When the user requests a registry of available peers (by typing \ids"), pull down the registry from
the registration server. The registry is the list of recently registered and potentially available
peers.
The message to request the registry should be:
SRC:###;DST:999;PNUM:5;HCT:1;MNUM:###;VL:;MESG:get map
The response (if there are no errors) will be:
SRC:999;DST:###;PNUM:6;HCT:1;MNUM:###;VL:;MESG:ids=###,###,###,###,...and###=ip@port,###=ip@port,...
2.3 Step #3, Send and Receive Data 
Implement the ability to send and receive short messages over UDP.
Loop waiting for either the user to ask to send a message (the \msg" command) or the \ids"
command.
2.4 Step #4, Serial Broadcast
Next, implement the ability to do serial broadcast. When a user requests to send a broadcast
message by typing \all" followed by a message, send one copy to every peer in your registry
which you have an IP/port address for (except yourself).
2.5 Step #5, Forwarding
In step 3, you implemented handling incoming messages with PNUM:3 that are to your peer ID.
Augment your peer code to handle PNUM:3 messages which you receive which are not addressed
to you (the DST value is not your peer's ID) by responding with a conrmation to the sender
(swap the message's original SRC/DST identiers and PNUM:4, HC:1 MESG:ACK) and then
forward the message you received.
cite from Dr. Genevieve Bartlett