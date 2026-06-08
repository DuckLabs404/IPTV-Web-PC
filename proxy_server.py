#!/usr/bin/env python3
"""
StreamBox Proxy Server v3
Execute: python proxy_server.py
Acesse:  http://localhost:8888
"""
import http.server, urllib.request, urllib.parse, os, threading, webbrowser
import socket, re, time, hashlib, gzip, json

PORT = 8888
PLAYER_FILE = "iptv-player.html"
BASE = f"http://localhost:{PORT}"

# ── Cache de playlist ────────────────────────────────────────────────────────
# Evita re-baixar 130MB toda vez — válido por CACHE_TTL segundos
CACHE_TTL = 300  # 5 minutos
_playlist_cache = {}   # url → {data: bytes, ts: float, lines: int}
_cache_lock = threading.Lock()

def cache_get(url):
    with _cache_lock:
        entry = _playlist_cache.get(url)
        if entry and (time.time() - entry['ts']) < CACHE_TTL:
            age = int(time.time() - entry['ts'])
            print(f"  💾 Cache hit ({age}s atrás, {entry['lines']} streams, {len(entry['data'])//1024}KB)")
            return entry['data']
    return None

def cache_set(url, data, lines):
    with _cache_lock:
        _playlist_cache[url] = {'data': data, 'ts': time.time(), 'lines': lines}

def cache_clear(url=None):
    with _cache_lock:
        if url:
            _playlist_cache.pop(url, None)
        else:
            _playlist_cache.clear()

# ── URL rewrite ──────────────────────────────────────────────────────────────
_url_pattern = re.compile(rb'^(https?://[^\s\r\n]+)', re.MULTILINE)

def rewrite_m3u(raw_bytes):
    """Reescreve URLs de stream para passar pelo proxy. Opera em bytes (mais rápido)."""
    proxy_prefix = (BASE + '/proxy?url=').encode()
    
    def replace(m):
        url = m.group(1)
        return proxy_prefix + urllib.parse.quote(url.decode('utf-8', errors='replace'), safe='').encode()
    
    return _url_pattern.sub(replace, raw_bytes)


class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args): pass  # silencia log padrão

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200); self.send_cors(); self.end_headers()

    def do_HEAD(self):
        path = self.path
        if path.startswith('/proxy'):
            qs = urllib.parse.urlparse(path).query
            params = urllib.parse.parse_qs(qs)
            target = params.get('url', [None])[0]
            if target:
                target = urllib.parse.unquote(target)
                try:
                    req = urllib.request.Request(
                        target, method='HEAD',
                        headers={'User-Agent': 'VLC/3.0.20'}
                    )
                    resp = urllib.request.urlopen(req, timeout=8)
                    self.send_response(resp.status)
                    self.send_cors(); self.end_headers()
                    return
                except urllib.error.HTTPError as e:
                    self.send_response(e.code); self.send_cors(); self.end_headers(); return
                except Exception:
                    self.send_response(502); self.send_cors(); self.end_headers(); return
        self.send_response(200); self.send_cors(); self.end_headers()

    def do_GET(self):
        p = self.path

        if p in ('/', '/iptv.html', ''):
            self._serve_file(); return

        if p.startswith('/playlist'):
            self._serve_playlist(); return

        if p.startswith('/cache/clear'):
            cache_clear()
            self.send_response(200); self.send_cors()
            self.send_header('Content-Type','text/plain'); self.end_headers()
            self.wfile.write(b'Cache cleared'); return

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

    # ── Serve player HTML ────────────────────────────────────────────────────
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

    # ── Playlist: baixa, reescreve e cacheia ─────────────────────────────────
    def _serve_playlist(self):
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        url = params.get('url', [None])[0]
        if not url:
            self.send_error(400, "url param required"); return
        url = urllib.parse.unquote(url)

        # ── Verifica cache primeiro ──────────────────────────────────────────
        cached = cache_get(url)
        if cached is not None:
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegurl; charset=utf-8")
            self.send_header("Content-Length", len(cached))
            self.send_header("X-Cache", "HIT")
            self.send_cors()
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try: self.wfile.write(cached)
            except Exception: pass
            return

        # ── Download ─────────────────────────────────────────────────────────
        t0 = time.time()
        print(f"  📋 Baixando: {url[:75]}...")
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'VLC/3.0.20 LibVLC/3.0.20',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
            })
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                enc = r.headers.get('Content-Encoding', '')
                if 'gzip' in enc:
                    raw = gzip.decompress(raw)
        except Exception as e:
            print(f"  ✗ Download: {e}")
            self.send_error(502, str(e)); return

        dl_time = time.time() - t0
        print(f"  ↓ {len(raw)//1024}KB em {dl_time:.1f}s — reescrevendo...")

        # ── Reescrita rápida em bytes ────────────────────────────────────────
        t1 = time.time()
        result = rewrite_m3u(raw)
        n_streams = result.count(b'/proxy?url=')
        rw_time = time.time() - t1
        print(f"  ✓ {n_streams:,} streams | {len(result)//1024}KB | reescrita {rw_time:.2f}s | total {time.time()-t0:.1f}s")

        # ── Salva no cache ───────────────────────────────────────────────────
        cache_set(url, result, n_streams)

        # ── Envia resposta ───────────────────────────────────────────────────
        self.send_response(200)
        self.send_header("Content-Type", "application/x-mpegurl; charset=utf-8")
        self.send_header("Content-Length", len(result))
        self.send_header("X-Cache", "MISS")
        self.send_cors()
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            # Envia em chunks para não travar
            chunk = 1024 * 1024  # 1MB por vez
            for i in range(0, len(result), chunk):
                self.wfile.write(result[i:i+chunk])
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ── Stream proxy ─────────────────────────────────────────────────────────
    def _stream_proxy(self, target):
        req = urllib.request.Request(target, headers={
            'User-Agent': 'VLC/3.0.20 LibVLC/3.0.20',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        })
        try:
            resp = urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as e:
            try: self.send_error(e.code)
            except: pass
            return
        except Exception as e:
            try: self.send_error(502, str(e))
            except: pass
            return

        ctype = resp.headers.get('Content-Type', 'video/mp2t')
        raw_url = target.lower().split('?')[0]
        if '.m3u8' in raw_url: ctype = 'application/vnd.apple.mpegurl'
        elif raw_url.endswith('.ts') or 'output=ts' in target or 'mpegts' in target: ctype = 'video/mp2t'
        elif raw_url.endswith('.mp4'): ctype = 'video/mp4'

        try:
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_cors()
            self.send_header("Cache-Control", "no-cache, no-store")
            self.end_headers()
        except Exception:
            resp.close(); return

        sent = 0
        try:
            while True:
                chunk = resp.read(131072)  # 128KB
                if not chunk: break
                self.wfile.write(chunk)
                sent += len(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            resp.close()


def main():
    print("=" * 58)
    print("   🎬  StreamBox Proxy Server v3")
    print("=" * 58)
    if not os.path.exists(PLAYER_FILE):
        print(f"\n  ⚠️  '{PLAYER_FILE}' NÃO encontrado!")
    else:
        print(f"\n  ✅ {PLAYER_FILE} encontrado")
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  💾 Cache de playlist: {CACHE_TTL}s (recarregar é instantâneo)")
    print(f"  Ctrl+C para parar\n" + "-"*58)

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), ProxyHandler)
    srv.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def open_once():
        import time; time.sleep(1.0)
        webbrowser.open(f'http://localhost:{PORT}')
    threading.Thread(target=open_once, daemon=True).start()

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  🛑 Encerrado.")

if __name__ == '__main__':
    main()