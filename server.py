import http.server
import socketserver
import socket
import os
import io
import sys

# Force UTF-8 for console output (Windows)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

PORT = 8080
GAME_DIR = os.path.dirname(os.path.abspath(__file__))

# Generate QR code PNG
def gen_qr(data):
    try:
        import qrcode
        from PIL import Image
        qr = qrcode.QRCode(border=2, box_size=10)
        qr.add_data(data)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        # Save to file
        out_path = os.path.join(GAME_DIR, 'qr-code.png')
        with open(out_path, 'wb') as f:
            f.write(buf.getvalue())
        print(f"  QR code saved: {out_path}")
        return buf.getvalue()
    except ImportError:
        print("  (qrcode not available, skip PNG)")
        return None

# Get local network IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

local_ip = get_local_ip()
game_url = f'http://{local_ip}:{PORT}/index.html'
print()
print('=' * 55)
print('  🧩 拼图游戏服务器已启动')
print(f'  局域网访问: {game_url}')
qr_data = gen_qr(game_url)
print(f'  本机访问:   http://127.0.0.1:{PORT}/index.html')
print('  Ctrl+C 停止服务器')
print('=' * 55)
print()

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GAME_DIR, **kwargs)

    def do_GET(self):
        # Serve landing page on root
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        return super().do_GET()

    def log_message(self, format, *args):
        quiet = self.path.endswith(('.jpg', '.png', '.ico'))
        if not quiet:
            print(f"  [{self.client_address[0]}] {args[0]} {args[1]} {args[2]}")

# Try to bind with SO_REUSEADDR
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), GameHandler) as httpd:
    httpd.allow_reuse_address = True
    httpd.serve_forever()
