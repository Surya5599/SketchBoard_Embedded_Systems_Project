import math, sys
C = math.cos(math.radians(30)); S = 1.9
W, H = 1800, 1700
OX, OY = 880, 1010
def P(x, y, z):
    return (OX + (x - y) * C * S, OY + (x + y) * 0.5 * S - z * S)
def pts(*ps): return " ".join(f"{a:.1f},{b:.1f}" for a, b in ps)
def shade(hexc, f):
    h = hexc.lstrip('#'); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))
out = []
def box(x, y, z, w, d, h, col, top=None, stroke=None, op=1):
    t = top or col
    sk = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ''
    s = f'<g opacity="{op}">'
    # left-front face (y = y+d)
    s += f'<polygon points="{pts(P(x,y+d,z),P(x+w,y+d,z),P(x+w,y+d,z+h),P(x,y+d,z+h))}" fill="{shade(col,0.62)}"{sk}/>'
    # right-front face (x = x+w)
    s += f'<polygon points="{pts(P(x+w,y,z),P(x+w,y+d,z),P(x+w,y+d,z+h),P(x+w,y,z+h))}" fill="{shade(col,0.8)}"{sk}/>'
    s += f'<polygon points="{pts(P(x,y,z+h),P(x+w,y,z+h),P(x+w,y+d,z+h),P(x,y+d,z+h))}" fill="{t}"{sk}/>'
    s += '</g>'
    out.append(s)
def plane(z, inner):
    tx, ty = P(0, 0, z)
    out.append(f'<g transform="matrix({C*S:.4f},{0.5*S:.4f},{-C*S:.4f},{0.5*S:.4f},{tx:.1f},{ty:.1f})">{inner}</g>')
def cyl(cx, cy, z, r, h, col, n=28):
    # approximate vertical cylinder: side band + top ellipse
    top = [P(cx + r*math.cos(a), cy + r*math.sin(a), z+h) for a in [2*math.pi*i/n for i in range(n)]]
    bot = [P(cx + r*math.cos(a), cy + r*math.sin(a), z) for a in [2*math.pi*i/n for i in range(n)]]
    # side: hull of visible half (angles where outward normal faces viewer: -45..135 deg)
    vis = [i for i in range(n) if math.cos(2*math.pi*i/n - math.radians(45)) > -0.05]
    side = [bot[i] for i in vis] + [top[i] for i in reversed(vis)]
    out.append(f'<polygon points="{pts(*side)}" fill="{shade(col,0.6)}"/>')
    out.append(f'<polygon points="{pts(*top)}" fill="{col}"/>')
def dome(cx, cy, z, r, col):
    cxs, cys = P(cx, cy, z)
    out.append(f'<ellipse cx="{cxs:.1f}" cy="{cys - r*S*0.55:.1f}" rx="{r*S*C*1.15:.1f}" ry="{r*S*0.95:.1f}" fill="url(#knob)"/>')
def guide(x, y, z0, z1, col="#7dd3fc"):
    a = P(x, y, z0); b = P(x, y, z1)
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="1.3" stroke-dasharray="5 5" opacity="0.55"/>')
def footprint(x, y, z, w, d, col="#38bdf8"):
    out.append(f'<polygon points="{pts(P(x,y,z),P(x+w,y,z),P(x+w,y+d,z),P(x,y+d,z))}" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-width="1.4" stroke-dasharray="6 4"/>')
def glass(z, col):
    out.append(f'<polygon points="{pts(P(14,8,z),P(276,8,z),P(276,224,z),P(14,224,z))}" fill="{col}" fill-opacity="0.06" stroke="{col}" stroke-opacity="0.45" stroke-width="1.2"/>')
callouts = []
def callout(x, y, z, side, ty, title, sub, col):
    callouts.append((P(x, y, z), side, ty, title, sub, col))

Z_BASE, Z_BB, Z_COMP, Z_DISP = 0, 75, 255, 430
BBH = 12

# ---------- base plate ----------
box(0, 0, Z_BASE, 300, 240, 6, "#1c1f26", stroke="#2a2f3a")

# guides base -> breadboard
for (x, y) in [(20, 14), (270, 14), (270, 218), (20, 218)]:
    guide(x, y, Z_BASE + 6, Z_BB, "#94a3b8")

# ---------- breadboard ----------
box(20, 14, Z_BB, 250, 204, BBH, "#e9e4d8", top="#f4f0e6", stroke="#cfc8b8")
holes = '''<defs><pattern id="h" width="4" height="4" patternUnits="userSpaceOnUse"><rect x="1.1" y="1.1" width="1.8" height="1.8" fill="#9b9384"/></pattern></defs>'''
bb = holes
# rails & terminal strips (rows along x)
for ry in (18, 62, 112, 162, 206):
    bb += f'<rect x="28" y="{ry}" width="234" height="8" fill="url(#h)"/>'
    bb += f'<line x1="28" y1="{ry-1.5}" x2="262" y2="{ry-1.5}" stroke="#ef4472" stroke-width="0.9"/>'
    bb += f'<line x1="28" y1="{ry+9.5}" x2="262" y2="{ry+9.5}" stroke="#3b82f6" stroke-width="0.9"/>'
for sy in (30, 74, 124, 174):
    bb += f'<rect x="28" y="{sy}" width="234" height="{28 if sy!=174 else 28}" fill="url(#h)"/>'
for gy in (45, 94, 145):
    pass
bb += '<rect x="26" y="57" width="238" height="3" fill="#ddd6c6"/><rect x="26" y="107" width="238" height="3" fill="#ddd6c6"/><rect x="26" y="157" width="238" height="3" fill="#ddd6c6"/>'
plane(Z_BB + BBH, bb)

# footprints of components on breadboard
TOPBB = Z_BB + BBH
fps = dict(
    nokia=(34, 67, 60, 60), chip=(110, 104, 68, 19), power=(178, 78, 46, 68),
    lcd=(64, 166, 115, 52), joy=(216, 165, 35, 48), isp=(167, 26, 23, 18),
    b1=(46, 176, 10, 10), b2=(188, 178, 10, 10), pot=(44, 158, 12, 12))
for k, (x, y, w, d) in fps.items():
    if k in ('nokia', 'lcd'): col = "#f472b6"
    else: col = "#38bdf8"
    footprint(x, y, TOPBB + 0.2, w, d, col)

# guides breadboard -> components
for k in ('chip', 'power', 'joy', 'isp', 'b1', 'b2', 'pot'):
    x, y, w, d = fps[k]
    for (gx, gy) in [(x, y), (x + w, y), (x + w, y + d), (x, y + d)] if k in ('chip', 'power', 'joy') else [(x + w/2, y + d/2)]:
        guide(gx, gy, TOPBB, Z_COMP)

# ---------- component layer ----------
glass(Z_COMP - 7, '#38bdf8')
comps = []
def add(order, fn): comps.append((order, fn))

def isp():
    x, y, w, d = fps['isp']
    box(x, y, Z_COMP, w, d, 2, "#1d4ed8", top="#2563eb")
    for i in range(3):
        for j in range(2):
            box(x + 5 + i*5, y + 3 + j*4, Z_COMP + 2, 2.4, 2.4, 9, "#111827")
add(fps['isp'][0] + fps['isp'][1], isp)

def chip():
    x, y, w, d = fps['chip']
    # pins
    for i in range(20):
        px = x + 2.2 + i * 3.25
        box(px, y - 2.2, Z_COMP - 6, 1.3, 2.4, 8, "#c0c7d2")
    box(x, y, Z_COMP, w, d, 5.5, "#1f2329", top="#2b3038")
    for i in range(20):
        px = x + 2.2 + i * 3.25
        box(px, y + d - 0.2, Z_COMP - 6, 1.3, 2.4, 8, "#c0c7d2")
    plane(Z_COMP + 5.5, f'<circle cx="{x+6}" cy="{y+9.5}" r="2.6" fill="#3b414b"/><circle cx="{x+w-7}" cy="{y+9.5}" r="2.6" fill="#3b414b"/>'
          f'<path d="M{x} {y+7} a2.5 2.5 0 0 1 0 5" fill="#16191e"/>'
          f'<text x="{x+14}" y="{y+8.5}" fill="#9aa3b2" font-family="Consolas,monospace" font-size="4.6" font-weight="bold">ATMEGA1284-PU</text>'
          f'<text x="{x+14}" y="{y+14}" fill="#6b7280" font-family="Consolas,monospace" font-size="3.4">AVR · 40-PIN DIP · 1746</text>')
add(fps['chip'][0] + fps['chip'][1], chip)

def power():
    x, y, w, d = fps['power']
    box(x, y, Z_COMP, w, d, 2, "#111318", top="#1a1d23")
    box(x + 22, y + 4, Z_COMP + 2, 14, 12, 10, "#0b0b0d")            # barrel jack
    box(x + 30, y + 22, Z_COMP + 2, 10, 10, 7, "#9ca3af")              # switch
    plane(Z_COMP + 9, f'<rect x="{x+32}" y="{y+24}" width="6" height="6" fill="#d1d5db"/>')
    box(x + 24, y + 44, Z_COMP + 2, 22, 16, 9, "#9aa0a8", top="#c4c9d0")  # USB-A
    plane(Z_COMP + 11, f'<rect x="{x+28}" y="{y+48}" width="14" height="8" fill="#6b7280"/>')
    for (jx, jy) in [(x + 5, y + 6), (x + 5, y + 26), (x + 11, y + 26), (x + 5, y + 54)]:
        box(jx, jy, Z_COMP + 2, 4, 6, 6, "#eab308", top="#facc15")
    cyl(x + 24, y + 36, Z_COMP + 2, 3, 7, "#111111")
    cyl(x + 37, y + 37, Z_COMP + 2, 1.8, 2.5, "#4ade80")
add(fps['power'][0] + fps['power'][1], power)

def pot():
    x, y, w, d = fps['pot']
    box(x, y, Z_COMP, w, d, 4, "#1e40af", top="#2563eb")
    cyl(x + 6, y + 6, Z_COMP + 4, 4, 2, "#e5e7eb")
    plane(Z_COMP + 6, f'<rect x="{x+3}" y="{y+5.4}" width="6" height="1.2" fill="#6b7280"/>')
add(fps['pot'][0] + fps['pot'][1], pot)

def button(k):
    def f():
        x, y, w, d = fps[k]
        box(x, y, Z_COMP, w, d, 4, "#9ca3af", top="#cbd5e1")
        cyl(x + 5, y + 5, Z_COMP + 4, 3, 3, "#111827")
    return f
add(fps['b1'][0] + fps['b1'][1], button('b1'))
add(fps['b2'][0] + fps['b2'][1], button('b2'))

def joy_base():
    x, y, w, d = fps['joy']
    box(x, y, Z_COMP, w, d, 2, "#0f1115", top="#16181d")
    for i in range(5):
        box(x + 6 + i * 5, y - 6, Z_COMP + 2, 3.5, 8, 6, "#1f2937")     # header
    box(x + 6, y + 10, Z_COMP + 2, 24, 24, 12, "#6b7280", top="#4b5563")  # gimbal
    plane(Z_COMP + 2, f'<text x="{x+3}" y="{y+42}" fill="#e5e7eb" font-family="Arial" font-size="3.4">X · Y · SW</text>')
add(fps['joy'][0] + fps['joy'][1], joy_base)

for _, fn in sorted(comps, key=lambda t: t[0]):
    fn()

# joystick knob
jx, jy = fps['joy'][0] + 18, fps['joy'][1] + 22
cyl(jx, jy, Z_COMP + 14, 3, 5, "#374151")
dome(jx, jy, Z_COMP + 21, 12, "#111111")

# guides components -> displays
for k in ('nokia', 'lcd'):
    x, y, w, d = fps[k]
    for (gx, gy) in [(x, y), (x + w, y), (x + w, y + d), (x, y + d)]:
        guide(gx, gy, TOPBB, Z_DISP, "#f472b6")

# ---------- display layer ----------
glass(Z_DISP - 9, '#f472b6')
def nokia():
    x, y, w, d = fps['nokia']
    for i in range(8):
        box(x + 14 + i * 4.2, y + 2, Z_DISP - 8, 1.6, 1.6, 8, "#d4d4d8")
    box(x, y, Z_DISP, w, d, 2, "#b91c1c", top="#dc2626")
    box(x + 5, y + 8, Z_DISP + 2, w - 10, d - 13, 4, "#a1a1aa", top="#d4d4d8")
    doodle = ("M8 40 q6 -14 12 -2 t12 0 t10 -6" )
    plane(Z_DISP + 6,
          f'<defs><radialGradient id="lcdg" cx="0.4" cy="0.4" r="0.8"><stop offset="0" stop-color="#e3f2c8"/><stop offset="1" stop-color="#a9c48a"/></radialGradient></defs>'
          f'<rect x="{x+8}" y="{y+11}" width="{w-16}" height="{d-21}" fill="url(#lcdg)"/>'
          f'<text x="{x+30}" y="{y+24}" text-anchor="middle" fill="#2f3a25" font-family="Consolas,monospace" font-size="6.6" font-weight="bold">SketchBoard</text>'
          f'<g transform="translate({x+8} {y+11})" fill="none" stroke="#2f3a25" stroke-width="1.2" stroke-linecap="square">'
          f'<path d="M5 30 l4 -6 l4 4 l5 -9 l5 7 l4 -3"/><circle cx="34" cy="23" r="4"/><path d="M28 31 h12"/>'
          f'<rect x="41.5" y="21.5" width="2" height="2" fill="#2f3a25" stroke="none"/></g>'
          + ''.join(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="#e5e7eb"/><circle cx="{cx}" cy="{cy}" r="1.2" fill="#7f1d1d"/>'
                    for cx, cy in [(x+3.5, y+3.5), (x+w-3.5, y+3.5), (x+3.5, y+d-3.5), (x+w-3.5, y+d-3.5)]))
def lcd():
    x, y, w, d = fps['lcd']
    for i in range(16):
        box(x + 12 + i * 3.2, y + 1.5, Z_DISP - 8, 1.4, 1.4, 8, "#d4d4d8")
    box(x, y, Z_DISP, w, d, 2, "#15803d", top="#16a34a")
    box(x + 7, y + 9, Z_DISP + 2, w - 14, d - 16, 6, "#111827", top="#1f2937")
    plane(Z_DISP + 8,
          f'<defs><linearGradient id="blu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b82f6"/><stop offset="1" stop-color="#1d4ed8"/></linearGradient></defs>'
          f'<rect x="{x+12}" y="{y+13}" width="{w-24}" height="{d-24}" fill="url(#blu)"/>'
          f'<text x="{x+40}" y="{y+24.5}" fill="#eef4ff" font-family="Consolas,monospace" font-size="8.5" font-weight="bold">&#9654;Sketch</text>'
          f'<text x="{x+47}" y="{y+34}" fill="#eef4ff" font-family="Consolas,monospace" font-size="8.5" font-weight="bold">View</text>'
          + ''.join(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="#eab308"/><circle cx="{cx}" cy="{cy}" r="1.1" fill="#14532d"/>'
                    for cx, cy in [(x+3.5, y+3.5), (x+w-3.5, y+3.5), (x+3.5, y+d-3.5), (x+w-3.5, y+d-3.5)])
          + f'<text x="{x+12}" y="{y+6.5}" fill="#dcfce7" font-family="Arial" font-size="2.6">VSS VDD V0 RS RW E D0 D1 D2 D3 D4 D5 D6 D7 A K</text>')
nokia(); lcd()

# ---------- callouts ----------
callout(64, 97, Z_DISP + 6, 'L', 200, "Nokia 5110 LCD", "84×48 sketch canvas · PORTB (SPI)", "#f472b6")
callout(120, 192, Z_DISP + 8, 'L', 330, "16×02 Character LCD", "menu: Sketch / View · PORTC + PORTD", "#f472b6")
callout(144, 113, Z_COMP + 5.5, 'L', 620, "ATmega1284 MCU", "ADC · EEPROM saves S1–S4", "#38bdf8")
callout(50, 164, Z_COMP + 6, 'L', 760, "Potentiometer", "LCD contrast", "#38bdf8")
callout(51, 181, Z_COMP + 7, 'L', 860, "Change-Selection button", "PA3", "#38bdf8")
callout(178, 35, Z_COMP + 11, 'R', 330, "AVR ISP adapter", "programming header", "#38bdf8")
callout(201, 112, Z_COMP + 10, 'R', 460, "Breadboard power module", "5 V / 3.3 V via USB", "#38bdf8")
callout(jx, jy, Z_COMP + 34, 'R', 200, "Analog 2-axis joystick", "PA0–PA2 · move / draw / erase", "#38bdf8")
callout(193, 183, Z_COMP + 7, 'R', 620, "Select button", "PA4", "#38bdf8")
callout(262, 120, Z_BB + BBH, 'R', 820, "Solderless breadboard", "", "#94a3b8")
callout(290, 200, Z_BASE + 6, 'R', 1000, "Base plate", "", "#94a3b8")

co = []
lay = []
for sd in 'LR':
    items = sorted([c for c in callouts if c[1] == sd], key=lambda c: c[0][1])
    last = 150
    for c in items:
        ty = max(c[0][1] - 40, last + 78)
        last = ty
        lay.append((c[0], sd, ty) + c[3:])
for (p, side, ty, title, sub, col) in lay:
    lx = 430 if side == 'L' else W - 400
    ex = lx + (14 if side == 'L' else -14)
    anchor = 'start' if side == 'R' else 'end'
    tx = lx - 0 if side == 'L' else lx
    co.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4" fill="{col}" stroke="#0b1020" stroke-width="1.5"/>')
    co.append(f'<polyline points="{p[0]:.1f},{p[1]:.1f} {ex:.1f},{ty} {lx:.1f},{ty}" fill="none" stroke="{col}" stroke-width="1.4" opacity="0.85"/>')
    dx = -8 if side == 'L' else 8
    co.append(f'<text x="{lx+dx}" y="{ty-3}" text-anchor="{anchor}" fill="#f8fafc" font-family="Segoe UI,Helvetica,Arial" font-size="19" font-weight="600">{title}</text>')
    if sub:
        co.append(f'<text x="{lx+dx}" y="{ty+19}" text-anchor="{anchor}" fill="#94a3b8" font-family="Segoe UI,Helvetica,Arial" font-size="14">{sub}</text>')

# layer tags
tags = [(Z_DISP, "03", "DISPLAYS"), (Z_COMP, "02", "INPUT · LOGIC · POWER"), (Z_BB, "01", "BREADBOARD")]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<radialGradient id="bg" cx="0.5" cy="0.45" r="0.75"><stop offset="0" stop-color="#1b2540"/><stop offset="1" stop-color="#070a13"/></radialGradient>
<radialGradient id="knob" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#5b6170"/><stop offset="0.45" stop-color="#1f2329"/><stop offset="1" stop-color="#050506"/></radialGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity="0.035"/></pattern>
<filter id="blur"><feGaussianBlur stdDeviation="22"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<ellipse cx="{P(150,120,0)[0]:.0f}" cy="{P(150,120,0)[1]+50:.0f}" rx="560" ry="150" fill="#000" opacity="0.55" filter="url(#blur)"/>
<text x="60" y="78" fill="#f8fafc" font-family="Segoe UI,Helvetica,Arial" font-size="40" font-weight="700" letter-spacing="1">SKETCHBOARD</text>
<text x="60" y="110" fill="#7dd3fc" font-family="Segoe UI,Helvetica,Arial" font-size="17" letter-spacing="4">EXPLODED VIEW · ATMEGA1284 ETCH-A-SKETCH</text>
<line x1="60" y1="128" x2="420" y2="128" stroke="#38bdf8" stroke-width="2"/>
{''.join(out)}
{''.join(co)}
<g font-family="Segoe UI,Helvetica,Arial">
<rect x="60" y="{H-92}" width="14" height="14" fill="#f472b6"/><text x="84" y="{H-80}" fill="#cbd5e1" font-size="15">Display layer footprint</text>
<rect x="290" y="{H-92}" width="14" height="14" fill="#38bdf8"/><text x="314" y="{H-80}" fill="#cbd5e1" font-size="15">Component footprint</text>
<text x="{W-60}" y="{H-50}" text-anchor="end" fill="#475569" font-size="14">Nokia 5110 · 16×02 LCD · 2-axis joystick · EEPROM save slots S1–S4</text>
</g>
</svg>'''
open(sys.argv[1], 'w').write(svg)
