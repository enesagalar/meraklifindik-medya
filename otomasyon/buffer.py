"""Buffer MCP'yi (https://mcp.buffer.com/mcp) doğrudan JSON-RPC ile çağırır. Anahtar ~/.claude.json'dan okunur, asla yazdırılmaz.
Kullanım:
  python otomasyon/buffer.py list                      # araçları listele
  python otomasyon/buffer.py call <arac> '<json args>' # aracı çağır (args dosyadan: @dosya.json)
"""
import json, sys, os, urllib.request

def cfg():
    # GitHub Actions: anahtar BUFFER_API_KEY secret'ından; yerelde ~/.claude.json (MCP ayarı)
    if os.environ.get('BUFFER_API_KEY'):
        return {"url": "https://mcp.buffer.com/mcp", "headers": {"Authorization": "Bearer " + os.environ['BUFFER_API_KEY'].strip()}}
    d = json.load(open(os.path.expanduser('~/.claude.json'), encoding='utf-8'))
    return d['mcpServers']['buffer']

C = cfg()
SID = None

def rpc(method, params=None, notify=False, _id=[0]):
    global SID
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None: body["params"] = params
    if not notify:
        _id[0] += 1; body["id"] = _id[0]
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", **C.get('headers', {})}
    if SID: h["Mcp-Session-Id"] = SID
    req = urllib.request.Request(C['url'], data=json.dumps(body).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        SID = r.headers.get("Mcp-Session-Id") or SID
        raw = r.read().decode('utf-8', 'replace')
    if notify or not raw.strip(): return None
    if raw.lstrip().startswith('{'): msg = json.loads(raw)
    else:  # SSE
        msg = None
        for line in raw.splitlines():
            if line.startswith('data:'):
                m = json.loads(line[5:].strip())
                if m.get('id') == body.get('id'): msg = m
    if msg and 'error' in msg: raise SystemExit(json.dumps(msg['error'], ensure_ascii=False))
    return msg['result'] if msg else None

def init():
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "findik-tools", "version": "1"}})
    rpc("notifications/initialized", notify=True)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    init()
    if sys.argv[1] == 'list':
        for t in rpc("tools/list")["tools"]:
            print(f"## {t['name']}\n{t.get('description','')[:400]}\nargs: {json.dumps(t.get('inputSchema',{}).get('properties',{}), ensure_ascii=False)[:1500]}\n")
    elif sys.argv[1] == 'call':
        a = sys.argv[3] if len(sys.argv) > 3 else '{}'
        args = json.load(open(a[1:], encoding='utf-8')) if a.startswith('@') else json.loads(a)
        res = rpc("tools/call", {"name": sys.argv[2], "arguments": args})
        for c in res.get('content', []):
            print(c.get('text', c))
        if res.get('isError'): sys.exit(1)
