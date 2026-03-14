from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

PASTE_FOLDER = "pastes"
os.makedirs(PASTE_FOLDER, exist_ok=True)


def next_id():
    files = os.listdir(PASTE_FOLDER)
    ids = []

    for f in files:
        if f.endswith(".txt"):
            try:
                ids.append(int(f.replace(".txt", "")))
            except:
                pass

    return max(ids, default=0) + 1


def counter_images(number):
    html = ""
    for digit in str(number):
        html += f'<img src="/digits/{digit}.gif">'
    return html


class PasteServer(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":

            total = len([f for f in os.listdir(PASTE_FOLDER) if f.endswith(".txt")])

            counter = counter_images(total)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = f"""
            <h2 style="text-align:center;">Pastebin</h2>

            <div style="text-align:center;">
            Total pastes:<br>
            {counter}
            </div>

            <br>
            <div style="text-align:center;">
            <form method="POST">
            <textarea name="text" rows="20" cols="80"></textarea><br>
            <input type="submit" value="Submit">
            </form>
            </div>
            """

            self.wfile.write(html.encode())


        elif self.path.startswith("/paste/"):

            paste_id = self.path.split("/")[-1]
            file_path = f"{PASTE_FOLDER}/{paste_id}.txt"

            if os.path.exists(file_path):

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()

                self.wfile.write(content.encode())

            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Paste not found")


        elif self.path.startswith("/digits/"):

            file_path = "." + self.path

            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-type", "image/gif")
                self.end_headers()

                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())

            else:
                self.send_response(404)
                self.end_headers()


    def do_POST(self):

        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode()

        parsed = urllib.parse.parse_qs(data)
        text = parsed.get("text", [""])[0]

        if text.strip() == "":
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Blank text")
            return

        paste_id = next_id()

        with open(f"{PASTE_FOLDER}/{paste_id}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write(f"Succesfully uploaded: /paste/{paste_id}".encode())


server = HTTPServer(("0.0.0.0", 8000), PasteServer)

print("Pastebin corriendo en puerto 8000")
server.serve_forever()
