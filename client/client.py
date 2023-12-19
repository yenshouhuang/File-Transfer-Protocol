# IS496: Computer Networks (Spring 2022)
# Programming Assignment 2 - Starter Code
# Name and Netid of each member:
# Member 1: Ken Wu (shwu2)
# Member 2: Thomas Huang (yenshuo2)
# Member 3: Jack Chuang (yzc2)

# Note: 
# This starter code is optional. Feel free to develop your own solution to Part 1. 
# The finished code for Part 1 can also be used for Part 2 of this assignment. 


# Import any necessary libraries below
import socket
import sys, argparse, os, struct
from typing import *

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from utils import *

BUFFER = 1048 # not used in part2
############## Beginning of Part 1 ##############

def part1 ():
    HOST = socket.gethostbyname(args.hostname)
    PORT = args.port
    sin = (HOST, PORT)

    # A dummy message (in bytes) to test the code
    message = args.message

    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('[ERROR] Failed to create socket.', e)
        sys.exit()

    conn.connect(sin)
    conn.sendall(message.encode())
    data = conn.recv(BUFFER)
    if data.decode() == "1":
        print("Acknowledgement: 1")
    else:
        print("Acknowledgement: 0")

    conn.close()

############## End of Part 1 ##############




############## Beginning of Part 2 ##############

def send_op_and_arg(conn: socket.socket, operation: str, arg: str="_"):
    msg = f"{operation:<{HEADERSIZE}}{len(arg):<{HEADERSIZE}}" + arg
    conn.sendall(msg.encode())


def part2 ():
    HOST = socket.gethostbyname(args.hostname)
    PORT = args.port
    sin = (HOST, PORT)

    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('[ERROR] Failed to create socket.', e)
        sys.exit()

    conn.connect(sin)

    while True:

        if (command := input("> ")) == "QUIT":
            send_op_and_arg(conn, command[:4])
            break


        elif (len(command) > 5 and command[:5] == "MKDIR"):
            send_op_and_arg(conn, command[:5], command[5:].strip())
            res = recvResponse(conn)

            print("The directory was successfully made" if res == "1" else
                  "Error in making directory" if res == "-1" else
                  "The directory already exists on server"
                 )


        elif (len(command) > 5 and command[:5] == "RMDIR"):
            send_op_and_arg(conn, command[:5], command[5:].strip())
            res = recvResponse(conn)
            if res == "-1": print("The directory does not exist on server")
            elif res == "-2": print("The directory is not empty")
            elif res == "1":
                ans = input("Are you sure? (Y/N): ").lower()
                if ans in ["y", "yes"]:
                    sendResponse(conn, "1")
                    res = recvResponse(conn)
                    print("Directory deleted" if res == "1" else
                          "Failed to delete directory"
                         )
                else:
                    if ans not in ["n", "no"]: 
                        print("unknown answer, abandoning operation")
                    sendResponse(conn, "-1")


        elif command == "LS":
            send_op_and_arg(conn, command[:2])
            data = recvDataStream(conn)
            print(data.decode())

        elif (len(command) > 2 and command[:2] == "DN"):
            filename = command[2:].strip()
            send_op_and_arg(conn, command[:2], filename)
            res = recvResponse(conn)
            if res == "-1":
                print("File does not exist on server")
                continue
            else:
                downloadFile(conn, filename)


        elif (len(command) > 2 and command[:2] == "UP"):
            filename = command[2:].strip()
            if not os.path.isfile(filename):
                print("File doesn't exist")
                continue
            send_op_and_arg(conn, command[:2], filename)

            uploadFile(conn, filename)


        elif (len(command) > 2 and command[:2] == "RM"):
            send_op_and_arg(conn, command[:2], command[2:].strip())
            res = recvResponse(conn)
            if res == "-1":
                print("File does not exist on server")
            else:
                ans = input("Are you sure? (Y/N): ").lower()
                if ans in ["y", "yes"]:
                    sendResponse(conn, "1")
                    res = recvResponse(conn)
                    print("File deleted" if res == "1" else
                          "Failed to delete File"
                         )
                else:
                    if ans not in ["n", "no"]: 
                        print("unknown answer, abandoning operation")
                    sendResponse(conn, "-1")


        elif (len(command) > 2 and command[:2] == "CD"):
            send_op_and_arg(conn, command[:2], command[2:].strip())
            res = recvResponse(conn)

            print("Changed current directory" if res == "1" else
                  "Error in changing directory" if res == "-1" else
                  "The directory does not exist on server"
                 )


        else:
            print("unknown command. try again")
            continue


        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple UDP")

    parser.add_argument("-hn", "--hostname", type=str, metavar="", default="127.0.0.1",
                        help="Remote hostname")
    parser.add_argument("-p", "--port", type=int, metavar="", default=9999,
                        help="port")
    parser.add_argument("-m", "--message", type=str, metavar="", default="Hello World",
                        help="message to be sent.")
    args = parser.parse_args()


    if len(sys.argv) == 1:
        part1()
    else:
        part2()

   
