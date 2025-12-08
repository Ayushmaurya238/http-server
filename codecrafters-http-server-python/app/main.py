import socket  # noqa: F401
import threading
import sys
import os
import gzip 
# import brotli

def choosecompression(accept_encoding):
    if accept_encoding=='':
        return None
    ae=accept_encoding.lower()
    
    if 'gzip' in ae:
        return 'gzip'
    return None
    
#get methods handling 
def notfound(client_socket , cmpmeth,flag):
    response1=(
        "HTTP/1.1 404 Not Found\r\n"
        "\r\n"
    )
    if flag:
        response1=(
        "HTTP/1.1 404 Not Found\r\n"
        "Connection:close\r\n"
        '\r\n'
        )
    
    client_socket.sendall(response1.encode())

def handleecho(client_socket,sttoecho, cmpmeth,flag):
    response2=(
        f"HTTP/1.1 200 OK\r\n"
        # header
        f"Content-Type:text/plain\r\n"
        f"Content-Length:{len(sttoecho.encode())}\r\n"
        '\r\n'
        # responsebody
        f'{sttoecho}'
    )
    if flag:
        response2=(
        f"HTTP/1.1 200 OK\r\n"
        # header
        f"Content-Type:text/plain\r\n"
        f"Content-Length:{len(sttoecho.encode())}\r\n"
        "Connection:close\r\n"
        '\r\n'
        # responsebody
        f'{sttoecho}'
        )
        
    cmp=choosecompression(cmpmeth)
    # print(cmp)
    bodybyte=sttoecho.encode()
    # print(type(bodybyte))
    if cmp :
        if cmp=='gzip':
            out=gzip.compress(bodybyte,6)
        
        res=(
        f"HTTP/1.1 200 OK\r\n"
        # header
        f'Content-Encoding:{cmp}\r\n'
        f"Content-Type:text/plain\r\n"
        f"Content-Length:{len(out)}\r\n"
        '\r\n'
        # responsebody
       
        )
        if flag:
            res=(
            f"HTTP/1.1 200 OK\r\n"
            # header
            f'Content-Encoding:{cmp}\r\n'
            f"Content-Type:text/plain\r\n"
            f"Content-Length:{len(out)}\r\n"
            "Connection:close\r\n"
        
            '\r\n'
            # responsebody
        
            )
        client_socket.sendall(res.encode()+out)
    else:

        client_socket.sendall(response2.encode())
    
def handleslash(client_socket, cmpmeth,flag):
    response3=(
        f"HTTP/1.1 200 OK\r\n\r\n"
    )
    if flag:
        response3=(
            f"HTTP/1.1 200 OK\r\n"
            "Connection:close\r\n"
            "\r\n"

        )
    
    client_socket.sendall(response3.encode())

def getUseragent(client_socket,useragent, cmpmeth,flag):
    response4=(
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(useragent.encode())}\r\n"
        f'\r\n'
        f'{useragent}'

    )
    if flag:
        response4=(
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(useragent.encode())}\r\n"
            "Connection:close\r\n"
            f'\r\n'
            f'{useragent}'

        )
    cmp=choosecompression(cmpmeth)
    bodybyte=useragent.encode()
    if cmp:
      
        if cmp=='gzip':
            out=gzip.compress(bodybyte,6)
        
        res=(
        f"HTTP/1.1 200 OK\r\n"
        # header
        f'Content-Encoding:{cmp}\r\n'
        f"Content-Type:text/plain\r\n"
        f"Content-Length:{len(out)}\r\n"
        '\r\n'
        
        
        )
        if flag:
            res=(
            f"HTTP/1.1 200 OK\r\n"
            # header
            f'Content-Encoding:{cmp}\r\n'
            f"Content-Type:text/plain\r\n"
            f"Content-Length:{len(out)}\r\n"
            "Connection: close\r\n"
            '\r\n'
            )
        client_socket.sendall(res.encode()+out)

    else:
        client_socket.sendall(response4.encode())
    
    


def handle_files(client_socket,file , cmpmeth,flag):
    f=open(file,'r')
    content=f.read()

    res=(
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: application/octet-stream\r\n"
        f"Content-Length: {len(content.encode())}\r\n"
        f'\r\n'
        f'{content}'
    )
    if flag:
        res=(
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(content.encode())}\r\n"
            "Connection: close\r\n"
            f'\r\n'
            f'{content}'
        )
    cmp=choosecompression(cmpmeth)
    bodybyte=content.encode()
    if cmp:
        
        if cmp=='gzip':
            out=gzip.compress(bodybyte,6)
        
        res=(
        f"HTTP/1.1 200 OK\r\n"
        # header
        f'Content-Encoding:{cmp}\r\n'
        f"Content-Type:text/plain\r\n"
        f"Content-Length:{len(out)}\r\n"
        '\r\n'
        
        )
        if flag:
            res=(
            f"HTTP/1.1 200 OK\r\n"
            # header
            f'Content-Encoding:{cmp}\r\n'
            f"Content-Type:text/plain\r\n"
            f"Content-Length:{len(out)}\r\n"
            "Connection:close\r\n"
            '\r\n'
            
            )
        client_socket.sendall(res.encode()+out)
    else :
        client_socket.sendall(res.encode())
    


# post request handle 

def writefile(path,reqbody,client_socket , cmpmeth,flag):
    with open(path,'w') as f:
        f.write(reqbody)
    resp=('HTTP/1.1 201 Created\r\n\r\n')
    if flag:
        resp=('HTTP/1.1 201 Created\r\n'
              "Connection:close\r\n"
              '\r\n')
    
    client_socket.sendall(resp.encode())


def handle_response(client_socket):

    buffer=b''
    keep_alive=True
    try:
        while keep_alive:
            # print('workn')
            while b'\r\n\r\n' not in buffer:
                chunk=client_socket.recv(4096)
                if not chunk:
                    keep_alive=False
                    break
                buffer=buffer+chunk
            if not buffer:
                break

            head,rest=buffer.split(b'\r\n\r\n',1)
            head_txt=head.decode(errors='ignore')
            headerlines=head_txt.split('\r\n')
            req_line=headerlines[0]
            print(headerlines)
            parts=req_line.split(' ',2)
            if len(parts)<2:
                keep_alive=False
                break
            method=parts[0]
            path=parts[1]
            headers={}
            flag=False

            for lines in headerlines[1:]:
                if ': ' in lines:
                    k,v=lines.split(': ',1)
                    headers[k.lower()]=v
                if 'Connection: close' in lines:
                    flag=True


            content_length = int(headers.get("content-length", "0"))
            while len(rest) < content_length:
                chunk = client_socket.recv(4096)
                if not chunk:
                    
                    break
                rest += chunk

            # extract the body bytes for this request
            body_bytes = rest[:content_length]
            # prepare buffer for subsequent requests that may already be received
            buffer = rest[content_length:]

            # gather commonly used values for your handlers
            # accept-encoding and user-agent from parsed headers
            acceptencode = headers.get("accept-encoding", "")
            useragent = headers.get("user-agent", "")

            # route & call your existing functions (mirror your previous logic)
            target = path
            endpoint = target.split("/")[1] if target.startswith("/") and len(target) > 1 else ""
            variable = target.split("/")[-1] if "/" in target else target

            if method == "GET":
                if target == "/":
                    handleslash(client_socket=client_socket, cmpmeth=acceptencode,flag=flag)
                elif endpoint == "user-agent":
                    getUseragent(client_socket=client_socket, useragent=useragent, cmpmeth=acceptencode,flag=flag)
                elif endpoint == "files":
                    # get directory arg safely
                    if "--directory" in sys.argv:
                        idx = sys.argv.index("--directory")
                        if idx + 1 < len(sys.argv):
                            directory = sys.argv[idx + 1]
                        else:
                            directory = ""
                    else:
                        directory = ""
                    cmpltpath = os.path.join(directory, variable.lstrip("/"))
                    if os.path.exists(cmpltpath):
                        handle_files(client_socket=client_socket, file=cmpltpath, cmpmeth=acceptencode,flag=flag)
                    else:
                        notfound(client_socket=client_socket, cmpmeth=acceptencode,flag=flag)
                elif endpoint == "echo":
                    handleecho(client_socket=client_socket, sttoecho=variable, cmpmeth=acceptencode,flag=flag)
                else:
                    notfound(client_socket=client_socket, cmpmeth=acceptencode,flag=flag)

            elif method == "POST":
                # If POST to /files/<name>, body_bytes contains the request body
                if endpoint == "files":
                    # convert body bytes to string (assuming tests send plain text)
                    reqbody = body_bytes.decode(errors="ignore")
                    if "--directory" in sys.argv:
                        idx = sys.argv.index("--directory")
                        directory = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
                    else:
                        directory = ""
                    cmpltpath = os.path.join(directory, variable.lstrip("/"))
                    writefile(cmpltpath, reqbody, client_socket, cmpmeth=acceptencode,flag=flag)
                else:
                    # unsupported POST -> 404
                    notfound(client_socket=client_socket, cmpmeth=acceptencode,flag=flag)
            

            # Decide whether to keep the connection alive.
            # If client explicitly asked Connection: close, we should close.
            conn_hdr = headers.get("connection", "")
            if conn_hdr.lower() == "close":
                keep_alive = False

            # otherwise, HTTP/1.1 defaults to keep-alive; continue loop to parse next request
    except Exception as e:
        # print for debugging (visible in CodeCrafters logs)
        print("Exception in connection handler:", e)
    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        client_socket.close()
        

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    #
    print(sys.argv)
    # print(sys.argv)
    
    server_socket = socket.create_server(("127.0.0.1", 4221), reuse_port=True)
    while True:
        server_socket.listen()
        print('server socket is listening...')
        client_socket,client_add=server_socket.accept()
        t=threading.Thread(target=handle_response,args=(client_socket,))

        
        t.start()
        

    # print()
if __name__ == "__main__":
    main()
