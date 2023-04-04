# Programming Assignment 2 (PG2) - TCP and FTP Program

IS496: Computer Networks (Spring 2023) \
Name and Netid of each member: \
Member 1: Ken Wu (shwu2) \
Member 2: Thomas Huang (yenshuo2) \
Member 3: Jack Chuang (yzc2)

## Background

We implement the client and server sides of a simple File Transfer Protocol (FTP) application in this programming assignment. TCP will be used for the file transfer, with the client determining the operation to be performed (creating a file, deleting a file, creating a new directory, removing a directory, changing to a different directory, obtaining a directory listing, or closing the connection). The server will respond to the specific command appropriately. This document contains specifics about the protocol.

## Preparation

```shell
import socket
import sys, argparse, subprocess, os
from typing import *
```

## Execution

Please connect to your student machines first.

```shell
$ ssh YOUR_NET_ID@student00.ischool.illinois.edu

$ ssh YOUR_TEAM_MEMBER_NET_ID@student01.ischool.illinois.edu
```

The server is running on student00, the client should be tested on student student01/student02/student03.

### Part 1: TCP Practice

In this part of the assignment, we built a simple TCP server and client where the server can successfully establish the connection with the client and send a string (e.g., "Hello World") to the client.

Run the socket server program.

```shell
YOUR_NET_ID@is-student00:~$ /YOUR_PATH/python3 server.py
```

Then the server terminal will show the messages below:

```
********** PART 1 **********
Waiting ...

```

Run the socket client program.

```shell
YOUR_TEAM_MEMBER_NET_ID@is-student01:~$ /YOUR_PATH/python3 client.py
```

Then the server terminal will receive the messages from the client, and reply the message below:

```
Client message: Hello World

```

The client side will receive the confirmation.

```
Acknowledgement: 1
```

### Part 2: FTP Program

Our implementation includes both the client and server sides of an FTP app that transfers files over TCP. The client is in charge of file creation, deletion, directory creation and removal, directory navigation, directory listing, and connection closure.

FTP client that takes in:

- The hostname of the server (argument 1).
- The port number on the server (argument 2).

FTP server that takes in:

- The hostname of the server (argument 1).
- The port number on the server (argument 2).

Run the socket server program.

```shell
YOUR_NET_ID@is-student00:~$ /YOUR_PATH/python3 server.py -hn [HOST_NAME] -p [PORT_NUMBER]
```

Then the terminal will show the messages below:

```
********** PART 2 **********
[INFO] Waiting for connection on port 9999...

```

Run the socket client program.

```shell
YOUR_TEAM_MEMBER_NET_ID@is-student01:~$ /YOUR_PATH/python3 client.py -hn [SERVER_HOST_NAME] -p [PORT_NUMBER]
```

Then the server terminal will show the messages below:

```
connection established
```

After connection established, client sends command to server; then server responds accordingly.


[DN]: If the received command is to download a file, the server will return the size of the file to the client as a 32-bit integer. The client will then prompt the user to confirm the download, and if confirmed, will save the file to disk and inform the user that the transfer was successful.

[UP]: If the received command is to upload a file, the client will send the length of the filename and the filename itself to the server. The server will then acknowledge that it is ready to receive the file. The client will then send the size of the file as a 32-bit value, followed by the file data itself. Once the file is received, the server will compute the throughput results for the transfer and send them back to the client. The client will display the throughput of the transfer.

`EXTRA CREDIT for DN and UP` If the specified file is large, sender divides the file based on specified BUFFER_SIZE to get the total count of packets. Sender then sends the information about this file to receiver first. Receiver confirms receiving basic information. Sender then starts sending all packets and md5 hash for receiver to validate data.

[RM/RMDIR]: If received command is to remove file/directory, server will ask the client again for confirmation. If "yes", server will remove the file/directory. Otherwise, client and server return to "prompt user for operation" and "wait for operation from client" state respectively.

[LS]: If received command is to list the directory on the server, server will obtains listing of it's directory, 
including both the permission settings and the name of each file.

[MKDIR]: If received command is to make directory, server will create a new folder with the specified name in the current directory or in the directory specified in the command.

[CD]: Server will check if the directory exists on server. If not, server sends "The directory does not exist on server". If exists, server changes its root directory.

[QUIT]: client and server both close their socket.

```
If client quits, server return to "[INFO] Waiting for connection on port 9999..."
```
