from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os
import random
import string

PASTE_FOLDER = "pastes"

os.makedirs(PASTE_FOLDER, exist_ok=True)

def random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

class PasteServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(b"""
            <h2>Pastebin</h2>
            <form method="POST">
            <textarea name="text" rows="20" cols="80"></textarea><br>
            <input type="submit" value="Upload">
            </form>
            """)

        elif self.path.startswith("/paste/"):
            paste_id = self.path.split("/")[-1]
            file_path = f"{PASTE_FOLDER}/{paste_id}.txt"

            if os.path.exists(file_path):
                with open(file_path) as f:
                    content = f.read()

                self.send_response(200)
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Error 404: Paste not found")

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode()

        parsed = urllib.parse.parse_qs(data)
        text = parsed["text"][0]

        paste_id = random_id()

        with open(f"{PASTE_FOLDER}/{paste_id}.txt", "w") as f:
            f.write(text)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"File uploaded to /paste/{paste_id}".encode())


server = HTTPServer(("0.0.0.0", 8000), PasteServer)
print("Pastebin running in port 8000")
server.serve_forever()
