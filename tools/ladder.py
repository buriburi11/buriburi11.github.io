"""Generates the portfolio's inline SVG figures (ladder diagrams + topology)."""
import math, html

def esc(s): return html.escape(s, quote=True)


def all_figs():
    return {"gateway": fig_gateway(), "udp": fig_udp(), "routes": fig_routes()}

class Ladder:
    def __init__(self, width, lanes, top=34, label_y=18):
        self.w = width; self.lanes = lanes; self.top = top; self.label_y = label_y
        self.items = []; self.i = 0; self.bottom = top

    def x(self, name): return self.lanes[name]

    def _head(self, x1, y1, x2, y2, size=7):
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - size * math.cos(a - 0.42), y2 - size * math.sin(a - 0.42))
        p2 = (x2 - size * math.cos(a + 0.42), y2 - size * math.sin(a + 0.42))
        return f'M{x2:.1f} {y2:.1f}L{p1[0]:.1f} {p1[1]:.1f}L{p2[0]:.1f} {p2[1]:.1f}Z'

    def msg(self, a, b, y, label, drop=None, cls="", dy=12, lpos=0.5, anchor="middle", lab_dy=-6, step=True):
        x1, x2 = self.x(a), self.x(b)
        y2 = y + dy
        if drop is not None:
            x2e = drop
            y2e = y + dy * (x2e - x1) / (x2 - x1)
        else:
            x2e, y2e = x2, y2
        lx = x1 + (x2e - x1) * lpos; ly = y + (y2e - y) * lpos + lab_dy
        parts = [f'<line x1="{x1}" y1="{y}" x2="{x2e:.1f}" y2="{y2e:.1f}" pathLength="1"/>']
        if drop is not None:
            c = 5
            parts.append(f'<path class="x" d="M{x2e-c:.1f} {y2e-c:.1f}l{2*c} {2*c}M{x2e+c:.1f} {y2e-c:.1f}l{-2*c} {2*c}"/>')
        else:
            sx = x2 - (6 if x2 > x1 else -6)
            parts.append(f'<path class="head" d="{self._head(x1, y, x2, y2)}"/>')
        if label:
            parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{esc(label)}</text>')
        k = f' style="--i:{self.i}"'
        self.items.append(f'<g class="m {cls}"{k}>' + "".join(parts) + '</g>')
        if step: self.i += 1
        self.bottom = max(self.bottom, y2)

    def note(self, lane, y, text, anchor="start", dx=8, cls="note", step=False):
        x = self.x(lane) + dx
        self.items.append(f'<g class="m n {cls}" style="--i:{self.i}"><text x="{x}" y="{y}" text-anchor="{anchor}">{esc(text)}</text></g>')
        if step: self.i += 1
        self.bottom = max(self.bottom, y)

    def raw(self, s, step=False):
        self.items.append(s.replace("{I}", str(self.i)))
        if step: self.i += 1

    def svg(self, title, desc, idp, height=None):
        h = height or self.bottom + 18
        lanes = []
        for name, x in self.lanes.items():
            lanes.append(f'<text class="lane" x="{x}" y="{self.label_y}" text-anchor="middle">{esc(name)}</text>'
                         f'<line class="life" x1="{x}" y1="{self.top - 8}" x2="{x}" y2="{h - 6}"/>')
        return (f'<svg class="ladder" viewBox="0 0 {self.w} {h}" role="img" aria-labelledby="{idp}-t {idp}-d" '
                f'xmlns="http://www.w3.org/2000/svg"><title id="{idp}-t">{esc(title)}</title>'
                f'<desc id="{idp}-d">{esc(desc)}</desc>' + "".join(lanes) + "".join(self.items) + '</svg>')


def fig_gateway():
    L = Ladder(400, {"client": 26, "gateway": 104, "time": 182, "whois": 252, "redis": 318, "model": 378}, top=34)
    # every label sits above its arrow's start point
    L.msg("client", "gateway", 50, "POST /chat", dy=10, lpos=0, anchor="start")
    L.msg("gateway", "time", 80, "connect", dy=8, lpos=0, anchor="start")
    L.msg("time", "gateway", 110, "4 bytes", dy=8, lpos=0, anchor="end")
    L.msg("gateway", "whois", 142, "alice\\r\\n", dy=12, lpos=0, anchor="start")
    L.msg("gateway", "redis", 170, "INCR", dy=12, lpos=0, anchor="start")
    L.raw('<g class="m n bracket" style="--i:{I}"><path d="M96 136v100"/><text x="90" y="182" text-anchor="end">in</text><text x="90" y="196" text-anchor="end">parallel</text></g>', step=True)
    L.msg("whois", "gateway", 204, "REGISTERED", dy=12, lpos=0, anchor="end")
    L.msg("redis", "gateway", 228, ":4", dy=12, lpos=0, anchor="end")
    L.raw('<g class="m n decide" style="--i:{I}"><rect x="104" y="254" width="150" height="24" rx="2"/><text x="112" y="270">4 ≤ 10 → allow</text></g>', step=True)
    L.msg("gateway", "model", 302, "query", dy=10, lpos=0, anchor="start")
    L.msg("model", "gateway", 336, "reply", dy=10, lpos=0, anchor="end")
    L.msg("gateway", "client", 368, "200 OK", dy=10, lpos=0, anchor="end")
    L.raw('<g class="m n" style="--i:{I}"><line class="sep" x1="8" y1="396" x2="392" y2="396"/></g>')
    L.msg("client", "gateway", 412, "", dy=10, cls="key")
    L.raw('<g class="m n" style="--i:{I}"><text x="112" y="426">×20 requests at once</text></g>')
    L.msg("gateway", "client", 446, "", dy=10, cls="key")
    L.raw('<g class="m n" style="--i:{I}"><text class="tag ok-t" x="112" y="452">×3 200 OK, admitted</text></g>')
    L.msg("gateway", "client", 476, "", dy=10, cls="lost")
    L.raw('<g class="m n" style="--i:{I}"><text class="tag" x="112" y="482">×17 429 Too Many Requests</text></g>', step=True)
    return L.svg("Figure 1: one request through the rate-limiting gateway, then a burst",
                 "A sequence diagram with six lifelines: client, gateway, time, whois, redis and model. "
                 "The client posts to /chat. The gateway reads a 4-byte timestamp from the Time server, then "
                 "queries WHOIS and sends INCR to Redis in parallel. WHOIS answers REGISTERED and Redis answers 4. "
                 "Since 4 is at most 10 the request is allowed, the gateway queries the model and returns 200 OK. "
                 "Below, 20 concurrent requests from one default-tier caller arrive; 3 receive 200 OK and 17 receive 429 Too Many Requests.",
                 "fig1", height=500)


def fig_udp():
    L = Ladder(400, {"sender": 40, "proxy": 200, "receiver": 360}, top=34)
    L.msg("sender", "receiver", 50, "DATA 4", dy=22, lpos=0, anchor="start")
    L.msg("receiver", "sender", 100, "ACK 4", dy=22, lpos=0, anchor="end")
    L.msg("sender", "receiver", 150, "DATA 5", dy=22, cls="lost", drop=200, lpos=0, anchor="start")
    L.note("proxy", 178, "dropped", dx=10, cls="lossnote", step=True)
    for k in range(5):
        L.msg("sender", "receiver", 198 + k * 7, "DATA 6–10" if k == 0 else "", dy=22, lpos=0, anchor="start", step=(k == 4))
    for k in range(3):
        L.msg("receiver", "sender", 270 + k * 7, "ACK 4 ×3 (duplicates)" if k == 0 else "", dy=22, cls="dup", lpos=0, anchor="end", step=(k == 2))
    L.note("sender", 326, "3rd duplicate → fast retransmit", dx=8, cls="callout", step=True)
    L.msg("sender", "receiver", 350, "DATA 5", dy=22, cls="key", lpos=0, anchor="start")
    for k in range(2):
        L.msg("receiver", "sender", 394 + k * 7, "ACK 4 ×2 (in flight)" if k == 0 else "", dy=22, cls="dup", lpos=0, anchor="end", step=(k == 1))
    L.msg("receiver", "sender", 446, "ACK 5", dy=22, lpos=0, anchor="end")
    L.note("sender", 494, "6–10 were discarded (Go-Back-N)", dx=8, step=True)
    L.note("sender", 512, "→ timer expires, resend 6–10", dx=8, step=True)
    return L.svg("Figure 2: recovering one lost segment",
                 "A sequence diagram with three lifelines: sender, proxy and receiver. DATA 4 is delivered and acknowledged. "
                 "DATA 5 is dropped at the proxy. DATA 6 through 10 arrive, and the receiver answers with duplicate ACK 4s. "
                 "On the third duplicate the sender fast-retransmits DATA 5; two more duplicates that were already in flight arrive, then ACK 5. "
                 "Because the receiver is Go-Back-N it had discarded segments 6 through 10, so they are resent after the retransmission timer expires.",
                 "fig2", height=526)


def fig_routes():
    # three small multiples of a 4-router topology, A->D path highlighted
    pos = {"A": (20, 70), "B": (75, 22), "C": (130, 70), "D": (180, 70)}
    links = [("A", "B", 1), ("B", "C", 2), ("A", "C", 5), ("C", "D", 1)]
    states = [
        ("generation 1", set(), [("A", "B"), ("B", "C"), ("C", "D")], "A → D: via B, cost 4"),
        ("generation 2: B–C down", {("B", "C")}, [("A", "C"), ("C", "D")], "A → D: via C, cost 6"),
        ("generation 3: A–C down", {("B", "C"), ("A", "C")}, [], "A → D: unreachable"),
    ]
    panels = []
    for k, (title, down, path, result) in enumerate(states):
        ox = 0; oy = k * 148
        g = [f'<g class="m panel" style="--i:{k}" transform="translate({ox},{oy})">']
        g.append(f'<text class="ptitle" x="0" y="0">{esc(title)}</text>')
        for a, b, c in links:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            onpath = (a, b) in path or (b, a) in path
            isdown = (a, b) in down or (b, a) in down
            cls = "link" + (" on" if onpath else "") + (" down" if isdown else "")
            g.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            off = 24 if (a, b) == ("A", "C") else -8
            dx = {("A", "B"): -12, ("B", "C"): 16}.get((a, b), 0)
            g.append(f'<text class="cost" x="{mx + dx:.0f}" y="{my + off:.0f}" text-anchor="middle">{c}</text>')
            if isdown:
                g.append(f'<path class="x" d="M{mx-5:.0f} {my-5:.0f}l10 10M{mx+5:.0f} {my-5:.0f}l-10 10"/>')
        for n, (x, y) in pos.items():
            g.append(f'<circle class="node{" end" if n in "AD" else ""}" cx="{x}" cy="{y}" r="9"/><text class="nl" x="{x}" y="{y + 4}" text-anchor="middle">{n}</text>')
        g.append(f'<text class="res" x="0" y="114">{esc(result)}</text>')
        g.append('</g>')
        panels.append("".join(g))
    return ('<svg class="topo" viewBox="-6 -16 240 446" role="img" aria-labelledby="fig3-t fig3-d" xmlns="http://www.w3.org/2000/svg">'
            '<title id="fig3-t">Figure 3: failover, then a partition</title>'
            '<desc id="fig3-d">Three snapshots of a four-router network with links A–B cost 1, B–C cost 2, A–C cost 5 and C–D cost 1. '
            'In generation 1 the route from A to D goes via B at cost 4. After the B–C link fails, generation 2 routes A to D via C at cost 6. '
            'After the A–C link also fails, generation 3 marks D unreachable from A.</desc>' + "".join(panels) + '</svg>')


if __name__ == "__main__":
    import sys, json
    out = all_figs()
    json.dump(out, open(sys.argv[1], "w"))
    print({k: len(v) for k, v in out.items()})
