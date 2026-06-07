#!/usr/bin/env python3
"""
StreamBox Proxy Server v2
Execute: python proxy_server.py
Acesse:  http://localhost:8888
"""
import http.server, urllib.request, urllib.parse, os, threading, webbrowser, socket, re

PORT = 8888
PLAYER_FILE = "iptv-player.html"
BASE = f"http://localhost:{PORT}"

class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args): pass  # silencia log base

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200); self.send_cors(); self.end_headers()

    def do_GET(self):
        p = self.path

        # ── / → player HTML ─────────────────────────────────────────────
        if p in ('/', '/iptv.html', ''):
            self._serve_file(); return

        # ── /playlist?url=... → reescreve M3U com URLs proxificadas ─────
        if p.startswith('/playlist'):
            self._serve_playlist(); return

        # ── /proxy?url=... → proxy de stream ────────────────────────────
        if p.startswith('/proxy'):
            qs = urllib.parse.urlparse(p).query
            params = urllib.parse.parse_qs(qs)
            target = params.get('url', [None])[0]
            if target:
                self._stream_proxy(urllib.parse.unquote(target))
            else:
                self.send_error(400)
            return

        self.send_error(404)

    def _serve_file(self):
        try:
            with open(PLAYER_FILE, 'rb') as f: data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(data))
            self.send_cors(); self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, f"{PLAYER_FILE} nao encontrado")

    def _serve_playlist(self):
        """Baixa o M3U e reescreve cada URL de stream para passar pelo proxy local"""
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        url = params.get('url', [None])[0]
        if not url:
            self.send_error(400, "url param required"); return
        url = urllib.parse.unquote(url)
        print(f"  📋 Baixando playlist: {url[:80]}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'VLC/3.0.20'})
            with urllib.request.urlopen(req, timeout=20) as r:
                content = r.read().decode('utf-8', errors='replace')
        except Exception as e:
            print(f"  ✗ Playlist error: {e}")
            self.send_error(502, str(e)); return

        # Reescreve cada linha de stream URL para /proxy?url=...
        lines = content.split('\n')
        out = []
        for line in lines:
            line_s = line.strip()
            if re.match(r'^https?://', line_s) or re.match(r'^rtmp', line_s):
                proxied = f"{BASE}/proxy?url={urllib.parse.quote(line_s, safe='')}"
                out.append(proxied)
            else:
                out.append(line)
        result = '\n'.join(out).encode('utf-8')

        print(f"  ✓ Playlist reescrita ({len(lines)} linhas)")
        self.send_response(200)
        self.send_header("Content-Type", "application/x-mpegurl")
        self.send_header("Content-Length", len(result))
        self.send_cors()
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(result)

    def _stream_proxy(self, target):
        print(f"  → {target[:85]}")
        req = urllib.request.Request(target, headers={
            'User-Agent': 'VLC/3.0.20 LibVLC/3.0.20',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        })
        try:
            resp = urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as e:
            print(f"  ✗ HTTP {e.code}: {target[:60]}")
            try: self.send_error(e.code)
            except: pass
            return
        except Exception as e:
            print(f"  ✗ {e}")
            try: self.send_error(502, str(e))
            except: pass
            return

        ctype = resp.headers.get('Content-Type', 'video/mp2t')
        if '.m3u8' in target or 'type=m3u' in target:
            ctype = 'application/vnd.apple.mpegurl'
        elif '.ts' in target or 'output=ts' in target or 'output=mpegts' in target:
            ctype = 'video/mp2t'

        try:
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_cors()
            self.send_header("Cache-Control", "no-cache, no-store")
            self.end_headers()
        except Exception:
            resp.close(); return

        print(f"  ✓ Streaming [{ctype.split('/')[-1]}]")
        sent = 0
        try:
            while True:
                chunk = resp.read(65536)
                if not chunk: break
                self.wfile.write(chunk)
                sent += len(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # normal ao trocar canal
        except Exception as e:
            print(f"  ! {type(e).__name__}")
        finally:
            resp.close()
            if sent: print(f"  ✓ Fim ({sent//1024} KB)")


def main():
    print("=" * 56)
    print("   🎬  StreamBox Proxy Server v2")
    print("=" * 56)
    if not os.path.exists(PLAYER_FILE):
        print(f"\n  ⚠️  '{PLAYER_FILE}' NÃO encontrado nesta pasta!")
        print(f"     Coloque os 2 arquivos na mesma pasta.\n")
    else:
        print(f"\n  ✅ {PLAYER_FILE} encontrado")
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  Ctrl+C para parar\n" + "-"*56)

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), ProxyHandler)
    srv.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    import time
    def open_once():
        time.sleep(1.0)
        webbrowser.open(f'http://localhost:{PORT}')
    threading.Thread(target=open_once, daemon=True).start()

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  🛑 Encerrado.")

if __name__ == '__main__':
    main()