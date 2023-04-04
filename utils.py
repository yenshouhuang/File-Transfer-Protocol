import socket, os, timeit, sys
from typing import *
from hashlib import md5

HEADERSIZE = 8
""" size of one header"""
BUFFER_SM, BUFFER_LG = 8, 2048


def sendResponse(conn: socket.socket, data: str):
    """ Send acknowledgement """
    package = f"{len(data):<{BUFFER_SM}}" + data
    conn.sendall(package.encode())

def recvResponse(conn: socket.socket) -> str:
    """ Receive acknowledgement """
    resSize, res, newResp = 0, "", True
    while True:
        data = conn.recv(BUFFER_SM)
        if newResp:
            resSize = int(data[:BUFFER_SM].decode().strip())
            newResp = False
            continue
        res += data.decode()
        if len(res) == resSize: break
    return res

def sendDataStream(conn: socket.socket, data: Union[str, bytes], verbose=False):
    data_encoded = data.encode() if type(data) == str else data
    
    if verbose: print("[INFO] sending size")
    size = len(data_encoded)

    size_packet = f"{size:<{BUFFER_SM}}".encode()
    conn.sendall(size_packet)

    if verbose: print("[INFO] waiting for size response")
    res = recvResponse(conn)
    if verbose: print("[INFO] received size response", res)

    if res != "1":
        print("[ERROR] receiver did not receive size packet")
        return

    i = 0
    while i * BUFFER_LG < size:
        packet = data_encoded[i * BUFFER_LG : (i+1) * BUFFER_LG]
        conn.sendall(packet)
        i += 1

def recvDataStream(conn: socket.socket, verbose=False) -> bytes:
    """ Receive a data stream """
    if verbose: print("[INFO] waiting for size")
    size = int(conn.recv(8).decode().strip())
    if verbose: print("[INFO] received size:", size)

    sendResponse(conn, "1")
    if verbose: print("[INFO] sent size response")

    data = b""
    while len(data) < size:
        data += conn.recv(BUFFER_LG)
    if verbose: print("[INFO] received full data")
    return data
    


def downloadFile(conn: socket.socket, filename: str, verbose=False):
    """
    Download file using buffer size
    """
    if verbose: print("[+] receiving file size")
    sendResponse(conn, "1")
    filesize = round(float(conn.recv(BUFFER_LG).decode()))
    
    received_size = 0
    with open(filename, "wb") as f:
        
        t1 = timeit.default_timer()

        while True:
            if verbose: print("\n[+] receiving chunkSize")
            chunkSize = int(conn.recv(BUFFER_SM).decode().strip())
            sendResponse(conn, "1")

            if verbose: print("[+] receiving chunk")
            bChunk = conn.recv(chunkSize)

            if verbose: print("[+] receiving MD5")
            hasher = md5()
            downloaded_md5Hash = conn.recv(32).decode()
            # print(downloaded_md5Hash)

            if verbose: print("[+] compare MD5s")
            hasher.update(bChunk)
            m_HashDigest = hasher.hexdigest()
            if m_HashDigest != downloaded_md5Hash:
                raise IOError(f"[ERROR] MD5 values don't match, \nm: {m_HashDigest}\nd: {downloaded_md5Hash}")
            
            if verbose: print("[+] send MD5 from received bytes")
            conn.sendall(m_HashDigest.encode())

            if verbose: print("[+] writing to file")
            f.write(bChunk)

            received_size += chunkSize
            print(f"{round(received_size / filesize * 100, 2)}%", end="\r")
            
            if received_size == filesize: break
        
        t2 = timeit.default_timer()
        print(f"Total bytes: {filesize}, Elapsed: {round(t2-t1, 2)} sec, Speed: {round(filesize / (t2-t1) / (1024 * 1024), 2)} MB/s")


def uploadFile(conn: socket.socket, filename: str, verbose=False):
    """
    Upload file using on buffer size
    """
    res = recvResponse(conn)
    if res == "1":
        if verbose: print("[+] sending file size")
        filesize = os.path.getsize(filename)
        conn.sendall(f"{filesize:<{BUFFER_LG}}".encode())

        sent_size = 0
        with open(filename, "rb") as f:
            
            t1 = timeit.default_timer()

            while True:
                if verbose: print("\n[+] reading chunk")
                bChunk = f.read(BUFFER_LG)
                if not bChunk: break
                
                if verbose: print("[+] sending chunk size")
                chunkSize = str(len(bChunk))
                size_msg = f"{chunkSize:<{BUFFER_SM}}".encode()
                conn.sendall(size_msg)
                res = recvResponse(conn)
                if res != "1": return # did not receive chunk size

                if verbose: print("[+] sending chunk")
                conn.sendall(bChunk)

                if verbose: print("[+] sending MD5 for chunk")
                hasher = md5()
                hasher.update(bChunk)
                conn.sendall(hasher.hexdigest().encode())
                # print(hasher.hexdigest())

                if verbose: print("[+] recevie and compare downloader's MP5Hash for chunk")
                receiver_md5Hash = conn.recv(32).decode()
                if receiver_md5Hash != hasher.hexdigest():
                    raise IOError("Receiver received incorrect data")

                sent_size += int(chunkSize)
                print(f"{round(sent_size / filesize * 100, 2)}%", end="\r")

            t2 = timeit.default_timer()
            print(f"Total bytes: {filesize}, Elapsed: {round(t2-t1, 2)} sec, Speed: {round(filesize / (t2-t1) / (1024 * 1024), 2)} MB/s")

