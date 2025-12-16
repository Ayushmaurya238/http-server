# 🚀 Custom HTTP Server (Python)

This project is a custom HTTP/1.1 server implemented from scratch in Python as part of the CodeCrafters **HTTP Server Challenge**.

The server handles routing, persistent connections, header parsing, file I/O, and Gzip compression — all without using any web frameworks.

---

### ✨ Features Implemented

#### ✔ HTTP/1.1 Request Parsing

- Parses request line (`GET /path HTTP/1.1`)
- Parses headers (case-insensitive)
- Supports reading request bodies using `Content-Length`
- Handles malformed or premature connection closures gracefully
---
#### ✔ Endpoints Implemented
1. **GET** `/`
Returns a basic HTTP 200 OK with an empty body.
```http
GET / HTTP/1.1

→ HTTP/1.1 200 OK
Content-Length: 0
```

---

2. **GET** `/echo/<string>`

Returns the string back in the response body.

Example:
```bash
GET /echo/hello

→ "hello"
```
Headers included:

- Content-Type: `text/plain`

- Content-Length: `<len(string)>`

---

3. **GET** /user-agent

Returns the value of the `User-Agent` header sent by the client.

Example:
```sql
GET /user-agent
User-Agent: mango/banana

→ "mango/banana"
```

---

4. **GET** `/files/<filename>`

Reads a file from a directory provided via:
```bash
$ ./your_program.sh --directory <path>
```
Responds with:

- `200 OK` + file content (as bytes, `application/octet-stream`)

- or `404 Not Found` if the file does not exist

---

5. **POST** `/files/<filename>`

Creates or overwrites a file inside the provided directory.

Request body = file contents.

Returns:

```http
HTTP/1.1 201 Created
```
---

#### ✔ Gzip Compression (`Accept-Encoding: gzip`)

Your server supports gzip compression on:
- `/echo/<string>`
- `/user-agent`
- `/files/<filename>` (if not a binary format like `.jpg`, `.png`, `.gz`, `.zip`)
- Any body larger than a small threshold (to avoid overhead)

If the client sends:
```makefile
Accept-Encoding: gzip
```
Your server replies with:
```makefile
Content-Encoding: gzip
Content-Length: <compressed_length>
```
And sends raw gzip-compressed bytes.

Compression is never applied if:

- Header missing
- File is already a compressed format
- Body is too small to benefit

---

#### ✔ Persistent Connections (HTTP/1.1)

The server supports multiple sequential requests over the same **TCP connection**.

It:
- Reads and buffers incoming data
- Parses one request at a time
- Responds
- Continues reading until the client closes the connection OR server chooses to close
---

#### ✔ Proper Connection: close Handling

If the client sends:
```pgsql
Connection: close
```



Your server:

1. Sends a response that includes
```pgsql
Connection: close
```
- Closes the **TCP connection** after responding
- Does not process additional requests on that connection (even if pipelined)

#### ✔ Thread-per-Connection Model

Each accepted client socket is served using a dedicated Python thread:
- Allows concurrent handling
- Matches CodeCrafters Stage for concurrency
- Thread closes after connection ends

---

#### 📂 Supported Directory Mode

Run the HTTP server with a directory argument:
```bash
./your_program.sh --directory /tmp/
```
Then:
- GET `/files/a.txt` → reads `/tmp/a.txt`
- POST `/files/a.txt` → writes `/tmp/a.txt`

This allows the server to act as a basic file-hosting endpoint.

---

#### 📜 Example Usage
**Echo endpoint**
```bash
curl http://localhost:4221/echo/blueberry
```
**Gzip response**
```bash
curl -H "Accept-Encoding: gzip" http://localhost:4221/echo/strawberry --output -
```
**User-Agent reflection**
```bash
curl http://localhost:4221/user-agent -H "User-Agent: grape/mango"
```
**Persistent connections**
```bash
curl --http1.1 -v http://localhost:4221/echo/apple \
     --next http://localhost:4221/user-agent -H "User-Agent: mango/orange"
```

**File upload**
```bash
echo "hello file" | curl -X POST --data-binary @- http://localhost:4221/files/a.txt
```
---
#### 🧠 Internal Architecture
1. **Byte Buffering for Persistent Connections**

The server maintains a buffer:
```arduino
buffer: bytes
```
It:
- Reads until it finds `\r\n\r\n` (end of headers)
- Parses headers
- Reads body using `Content-Length`
- Removes consumed bytes from buffer
- Continues parsing if more requests are already present

2. **Manual Header Assembly**

Responses are built manually:
```python 
headers = "HTTP/1.1 200 OK\r\n"
headers += f"Content-Length: {len(body)}\r\n"
headers += "\r\n"
sock.sendall(headers.encode() + body)
```

3. **Binary-Safe File Operations**

Files served using:
```python
open(filename, "r")
```
---
#### 📌 Requirements
- Python ≥ 3.10
- No web frameworks
- Raw sockets only
---

#### 📜 License

MIT License — free to use, modify, distribute.

---
