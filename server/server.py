# IS496: Computer Networks (Spring 2022)
# Programming Assignment 2 - Starter Code
# Name and Netid of each member:
# Member 1: Ken Wu (shwu2)
# Member 2: Thomas Huang (yenshuo2)
# Member 3: Jack Chuang (yzc2)

import socket
import sys, argparse, subprocess, os
from typing import *

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from utils import *

BUFFER = 1048 # not used in part2
############## Beginning of Part 1 ##############

def part1 ():
    print("********** PART 1 **********")
    HOST = args.hostname
    PORT = args.port
    sin = (HOST, PORT)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('[ERROR] Failed to create socket.', e)
        sys.exit()

    try:
        server.bind(sin)
    except socket.error as e:
        print('[ERROR] Failed to bind socket.', e)
        sys.exit()

    server.listen()
    print(f"[INFO] Listening on port {PORT}...")
    
    conn, addr = server.accept()

    try:
        with conn:
            while True:
                data = conn.recv(BUFFER)
                if not data: break
                elif data.decode() == "Hello World":
                    print(f"Client Message: {data.decode()}")
                    conn.sendall("1".encode())
                else:
                    conn.sendall("0".encode())
    except KeyboardInterrupt as e:
        print("\nShutting down server")
        server.close()

############## End of Part 1 ##############




############## Beginning of Part 2 ##############



def part2 ():
    print("********** PART 2 **********")
    HOST = args.hostname
    PORT = args.port
    sin = (HOST, PORT)

    try:
        mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('[ERROR] Failed to create socket.', e)
        sys.exit()
        
    try:
        mSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:
        print('[ERROR] Failed to set socket option.', e)
        sys.exit()
    
    try:
        mSocket.bind(sin)
    except socket.error as e:
        print('[ERROR] Failed to bind socket.', e)
        sys.exit()

    mSocket.listen()

    try:
        while True:
            print(f"[INFO] Waiting for connection on port {PORT}...")
            conn, addr = mSocket.accept()
            with conn:
                print("connection established")
                while True:
                    # ◼︎ receive new command
                    op, argsize, arg = "", 0, ""
                    newCmd = True
                    while True:
                        msg = conn.recv(HEADERSIZE * 2)
                        if newCmd:
                            op = msg[:8].decode().strip()
                            argsize = int(msg[8:].strip())
                            newCmd = False
                            continue
                        arg += msg.decode()
                        if len(arg) == argsize or argsize == 0: break

                    # ◼︎ execute command
                    if op == "QUIT":
                        break

                    elif op == "LS":
                        output = subprocess.getoutput("ls -la")
                        sendDataStream(conn, output)

                    elif (len(op) == 2 and op[:2] == "DN"):
                        if not os.path.isfile(arg): sendResponse(conn, "-1")
                        else:
                            sendResponse(conn, "1")
                            uploadFile(conn, arg)

                    elif (len(op) == 2 and op[:2] == "UP"):
                        downloadFile(conn, arg)

                    elif (len(op) == 2 and op[:2] == "RM"):
                        if not os.path.isfile(arg): sendResponse(conn, "-1")
                        else:
                            sendResponse(conn, "1")
                            ans = recvResponse(conn)
                            if ans == "1":
                                try:
                                    os.remove(arg)
                                    sendResponse(conn, "1")
                                except:
                                    sendResponse(conn, "-1")

                    elif (len(op) == 2 and op[:2] == "CD"):
                        if not os.path.isdir(arg): sendResponse(conn, "-2")
                        else:
                            try:
                                os.chdir(arg)
                                sendResponse(conn, "1")
                            except:
                                sendResponse(conn, "-1")

                    elif (len(op) == 5 and op[:5] == "MKDIR"):
                        if os.path.isdir(arg): sendResponse(conn, "-2")
                        else:
                            try:
                                os.mkdir(arg)
                                sendResponse(conn, "1")
                            except:
                                sendResponse(conn, "-1")

                    elif (len(op) == 5 and op[:5] == "RMDIR"):
                        if not os.path.isdir(arg): sendResponse(conn, "-1")
                        else:
                            if os.listdir(arg): sendResponse(conn, "-2")
                            else: 
                                sendResponse(conn, "1")
                                ans = recvResponse(conn)
                                if ans == "1":
                                    try:
                                        os.rmdir(arg)
                                        sendResponse(conn, "1")
                                    except:
                                        sendResponse(conn, "-1")
                    
                    else:
                        print("unknown operation from client.")
                        continue

    except KeyboardInterrupt:
        print("\nShutting down server manually")
    mSocket.close()

############## End of Part 2 ##############



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TCP")
    parser.add_argument("-hn", "--hostname", type=str, metavar="", default="127.0.0.1",
                        help="Hostname")
    parser.add_argument("-p", "--port", type=int, metavar="", default=9999, # should be 80
                        help="port")
    parser.add_argument("-r", "--response", type=str, metavar="", default="Server response.",
                        help="Response to be sent.")
    args = parser.parse_args()
    

    if len(sys.argv) == 1:
        part1()
    else:
        part2()