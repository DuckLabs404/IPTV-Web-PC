#!/usr/bin/env python3
"""
StreamBox Proxy Server
Execute: python proxy_server.py
Acesse: http://localhost:8888
"""
import http.server, urllib.request, urllib.parse, sys, os, threading, webbrowser

PORT = 8888
PLAYER_FILE = "iptv-player.html"

class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Silencia logs repetitivos, só mostra erros
        if args and str(args[1]) not in ('200','206','304'):
            print(f"  [{args[1]}] {args[0]}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        path = self.path

        # ── Serve o player HTML ──────────────────────────────────────────
        if path in ('/', '/iptv.html', '/player', ''):
            try:
                with open(PLAYER_FILE, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(data))
                self.send_cors()
                self.end_headers()
                if not head_only:
                    self.wfile.write(data)
            except FileNotFoundError:
                self.send_error(404, f"Arquivo {PLAYER_FILE} não encontrado na mesma pasta")
            return

        # ── Proxy de stream: /proxy?url=http://... ───────────────────────
        if path.startswith('/proxy'):
            qs = urllib.parse.urlparse(path).query
            params = urllib.parse.parse_qs(qs)
            target = params.get('url', [None])[0]

            if not target:
                self.send_error(400, "Parâmetro 'url' necessário")
                return

            target = urllib.parse.unquote(target)
            print(f"  🔀 Proxy: {target[:80]}...")

            try:
                req = urllib.request.Request(
                    target,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VLC/3.0',
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    ctype = resp.headers.get('Content-Type', 'application/octet-stream')
                    clen  = resp.headers.get('Content-Length', '')

                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    if clen:
                        self.send_header("Content-Length", clen)
                    self.send_cors()
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()

                    if head_only:
                        return

                    # Streaming chunk por chunk (não carrega tudo na memória)
                    while True:
                        chunk = resp.read(65536)  # 64KB
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError):
                            break  # Cliente fechou a conexão (normal ao trocar canal)

            except urllib.error.HTTPError as e:
                print(f"  ❌ HTTP {e.code}: {target[:60]}")
                self.send_error(e.code, str(e))
            except urllib.error.URLError as e:
                print(f"  ❌ URL Error: {e.reason}")
                self.send_error(502, f"Upstream error: {e.reason}")
            except Exception as e:
                print(f"  ❌ Erro: {e}")
                self.send_error(500, str(e))
            return

        # ── 404 para outras rotas ────────────────────────────────────────
        self.send_error(404)


def main():
    print("=" * 52)
    print("  🎬  StreamBox Proxy Server")
    print("=" * 52)
    print(f"  Porta:   {PORT}")
    print(f"  Player:  {PLAYER_FILE}")
    print(f"  URL:     http://localhost:{PORT}")
    print()

    if not os.path.exists(PLAYER_FILE):
        print(f"  ⚠️  ATENÇÃO: '{PLAYER_FILE}' não encontrado!")
        print(f"     Coloque o proxy_server.py na mesma pasta que o iptv-player.html")
        print()

    server = http.server.ThreadingHTTPServer(('', PORT), ProxyHandler)
    print(f"  ✅ Servidor rodando em http://localhost:{PORT}")
    print(f"  ℹ️  Pressione Ctrl+C para parar\n")

    # Abre o navegador automaticamente após 1s
    def open_browser():
        import time; time.sleep(1.2)
        webbrowser.open(f'http://localhost:{PORT}')
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  🛑 Servidor encerrado.")

if __name__ == '__main__':
    main()