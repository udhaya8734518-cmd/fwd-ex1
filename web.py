from http.server import HTTPServer, BaseHTTPRequestHandler
content = """
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TCP & IP Address — Interactive Demo</title>
  <style>
    :root{--bg:#0f1724;--card:#0b1220;--accent:#06b6d4;--muted:#94a3b8;--glass:rgba(255,255,255,0.03)}
    body{font-family:Inter,system-ui,Arial;background:linear-gradient(180deg,#081226 0%, #07121a 100%);color:#e6eef6;margin:0;padding:24px}
    .container{max-width:980px;margin:0 auto}
    h1{font-size:28px;margin:0 0 8px}
    p.lead{color:var(--muted);margin-top:0}
    .grid{display:grid;grid-template-columns:1fr 360px;gap:20px;margin-top:18px}
    .card{background:var(--card);padding:16px;border-radius:12px;box-shadow:0 6px 20px rgba(2,6,23,0.6);}
    label{display:block;margin-bottom:6px;color:var(--muted);font-size:13px}
    input[type=text], input[type=number], select{width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:var(--glass);color:inherit}
    button{background:var(--accent);border:none;padding:10px 12px;border-radius:8px;color:#012;cursor:pointer;margin-top:10px}
    pre{background:#020617;padding:12px;border-radius:8px;overflow:auto}
    .small{font-size:13px;color:var(--muted)}
    .row{display:flex;gap:10px}
    .tcp-box{font-family:monospace;background:linear-gradient(90deg,#021123,#041728);padding:12px;border-radius:10px}
    .handshake{margin-top:12px}
    .msg{padding:8px;border-radius:8px;margin-bottom:8px;background:rgba(255,255,255,0.02)}
    .ok{color:#10b981}
    footer{margin-top:20px;color:var(--muted);font-size:13px}
    @media (max-width:880px){.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <div class="container">
    <h1>TCP & IP Address — Interactive Demo</h1>
    <p class="lead">Learn about IP addresses and TCP with small interactive tools: an IP validator, TCP packet builder, and a simulated TCP 3‑way handshake.</p><div class="grid">
  <div>
    <div class="card">
      <h3>1) IP Address Validator</h3>
      <label for="ip">Enter IPv4 address</label>
      <input id="ip" type="text" placeholder="e.g. 192.168.0.1" />
      <div class="row">
        <button id="checkIp">Validate</button>
        <button id="classifyIp">Classify (A/B/C/...)</button>
      </div>
      <p id="ipResult" class="small"></p>
      <hr />
      <h3>2) TCP Packet Builder</h3>
      <label>Source Port</label>
      <input id="sport" type="number" min="1" max="65535" value="54321" />
      <label>Destination Port</label>
      <input id="dport" type="number" min="1" max="65535" value="80" />
      <label>Sequence Number</label>
      <input id="seq" type="number" value="1000" />
      <label>Acknowledgement Number</label>
      <input id="ack" type="number" value="0" />
      <label>Flags</label>
      <select id="flags">
        <option value="SYN">SYN</option>
        <option value="SYN,ACK">SYN,ACK</option>
        <option value="ACK">ACK</option>
        <option value="FIN">FIN</option>
      </select>
      <button id="buildTcp">Build TCP Packet</button>
      <pre id="tcpOutput" class="tcp-box">// TCP packet will appear here</pre>

      <hr />
      <h3>3) Simulate TCP 3-way Handshake</h3>
      <p class="small">Click to simulate a client connecting to a server (SYN → SYN/ACK → ACK).</p>
      <button id="startHandshake">Start Handshake</button>
      <div id="handshakeLog" class="handshake"></div>
    </div>

    <div style="height:12px"></div>

    <div class="card">
      <h3>Quick Reference</h3>
      <p class="small"><strong>IP (Internet Protocol)</strong> — provides addressing and routing so packets get from source to destination. Example: <code>192.168.1.10</code>.</p>
      <p class="small"><strong>TCP (Transmission Control Protocol)</strong> — provides reliable, ordered, connection‑oriented delivery of bytes. Uses ports to distinguish services (HTTP typically uses port 80/443).</p>
    </div>
  </div>

  <aside>
    <div class="card">
      <h3>Why validate?</h3>
      <p class="small">Validating an IP helps ensure inputs are correct before using them in network tools. This demo validates <em>IPv4 dotted-decimal</em> format and classifies the common class A/B/C ranges.</p>
    </div>

    <div style="height:12px"></div>

    <div class="card">
      <h3>TCP Packet View</h3>
      <pre id="tcpView">-- TCP Header --

SrcPort: - DstPort: - SeqNum: - AckNum: - Flags: - Window: 65535 Checksum: 0x0000</pre> </div>

<div style="height:12px"></div>

    <div class="card">
      <h3>Notes</h3>
      <ul class="small">
        <li>Ports range from 1 to 65535.</li>
        <li>IP classes are legacy but help with quick classification.</li>
        <li>This is a learning tool — it does <strong>not</strong> send real network packets.</li>
      </ul>
    </div>
  </aside>
</div>

<footer>Made for learning • Edit the HTML to expand features</footer>

  </div>  <script>
    // IP validator: checks dotted quad and gives basic class
    function isValidIPv4(ip){
      const parts = ip.split('.');
      if(parts.length!==4) return false;
      for(const p of parts){
        if(!/^[0-9]+$/.test(p)) return false;
        const n = Number(p);
        if(n<0 || n>255) return false;
        // no leading zeros unless '0'
        if(p.length>1 && p.startsWith('0')) return false;
      }
      return true;
    }
    function ipClass(ip){
      try{
        const first = Number(ip.split('.')[0]);
        if(first>=1 && first<=126) return 'A';
        if(first>=128 && first<=191) return 'B';
        if(first>=192 && first<=223) return 'C';
        if(first>=224 && first<=239) return 'D (multicast)';
        if(first>=240 && first<=254) return 'E (reserved)';
        return 'Unknown';
      }catch(e){return 'Invalid'}
    }

    document.getElementById('checkIp').addEventListener('click', ()=>{
      const ip = document.getElementById('ip').value.trim();
      const res = document.getElementById('ipResult');
      if(isValidIPv4(ip)){
        res.innerHTML = <span class="ok">Valid IPv4 address</span> — class ${ipClass(ip)};
      } else {
        res.textContent = 'Not a valid IPv4 dotted-decimal address.';
      }
    });

    document.getElementById('classifyIp').addEventListener('click', ()=>{
      const ip = document.getElementById('ip').value.trim();
      const res = document.getElementById('ipResult');
      if(isValidIPv4(ip)) res.textContent = Class: ${ipClass(ip)};
      else res.textContent = 'Enter a valid IPv4 address first.';
    });

    // Build a simple TCP packet representation
    function buildTcpPacket(){
      const sport = Number(document.getElementById('sport').value)||0;
      const dport = Number(document.getElementById('dport').value)||0;
      const seq = Number(document.getElementById('seq').value)||0;
      const ack = Number(document.getElementById('ack').value)||0;
      const flags = document.getElementById('flags').value;
      const pkt = {
        srcPort: sport,
        dstPort: dport,
        seqNum: seq,
        ackNum: ack,
        flags: flags,
        window: 65535,
        checksum: '0x' + (Math.floor(Math.random()*0xffff)).toString(16).padStart(4,'0')
      };
      return pkt;
    }

    function renderTcp(pkt){
      const out = SrcPort: ${pkt.srcPort}\nDstPort: ${pkt.dstPort}\nSeqNum: ${pkt.seqNum}\nAckNum: ${pkt.ackNum}\nFlags: ${pkt.flags}\nWindow: ${pkt.window}\nChecksum: ${pkt.checksum};
      document.getElementById('tcpOutput').textContent = out;
      document.getElementById('tcpView').textContent = -- TCP Header --\nSrcPort: ${pkt.srcPort}\nDstPort: ${pkt.dstPort}\nSeqNum: ${pkt.seqNum}\nAckNum: ${pkt.ackNum}\nFlags: ${pkt.flags}\nWindow: ${pkt.window}\nChecksum: ${pkt.checksum};
    }

    document.getElementById('buildTcp').addEventListener('click', ()=>{
      const pkt = buildTcpPacket();
      renderTcp(pkt);
    });

    // Simple handshake simulation
    function logHand(msg){
      const div = document.createElement('div');
      div.className = 'msg';
      div.textContent = msg;
      document.getElementById('handshakeLog').prepend(div);
    }

    document.getElementById('startHandshake').addEventListener('click', ()=>{
      const log = document.getElementById('handshakeLog');
      log.innerHTML = '';
      logHand('Client → Server: [SYN] (seq=1000)');
      // SYN/ACK after short delay
      setTimeout(()=>{
        logHand('Server → Client: [SYN,ACK] (seq=2000, ack=1001)');
      },700);
      // Final ACK
      setTimeout(()=>{
        logHand('Client → Server: [ACK] (ack=2001) — Connection established');
      },1400);
    });

    // build initial view
    renderTcp(buildTcpPacket());
  </script></body>
</html>
"""
class myhandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("request received")
        self.send_response(200)
        self.send_header('content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode())
server_address = ('',8000)
httpd = HTTPServer(server_address,myhandler)
print("my webserver is running...")
httpd.serve_forever()