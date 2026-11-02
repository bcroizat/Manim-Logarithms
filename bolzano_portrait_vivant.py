import sys, subprocess, numpy as np, cv2

# Portrait vivant de Bernard Bolzano (env. 15 s, clin d'oeil final)
# Usage : python bolzano_portrait_vivant.py bolzano.jpg render Bolzano_portrait_vivant.mp4
#         python bolzano_portrait_vivant.py bolzano.jpg preview 3.0 13.2
S = 1080 / 329               # orig 250x329 -> 822x1080
W, H = 822, 1080
FPS, DUR = 30, 15.0
LID_END = 1.3     # jusqu'où descend la paupière fermée (en rayons d'oeil sous le centre)
src = cv2.imread(sys.argv[1])
base = cv2.resize(src, (W, H), interpolation=cv2.INTER_LANCZOS4)
blur = cv2.GaussianBlur(base, (0, 0), 2.0)
base = cv2.addWeighted(base, 1.35, blur, -0.35, 0)     # light sharpening
base = base.astype(np.float32)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

# ---------- eyes (orig coords) ----------
EYES = [dict(c=(85.8, 118.5), r=(4.6, 2.9)), dict(c=(118.8, 118.3), r=(5.4, 3.0))]
for e in EYES:
    cx, cy = e['c'][0] * S, e['c'][1] * S
    rx, ry = e['r'][0] * S, e['r'][1] * S
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    e['mask'] = 1 - smoothstep(1.25, 2.1, d)                    # feathered eye area
    e['iris'] = np.exp(-(((xx - cx) / (2.4 * S)) ** 2 + ((yy - cy) / (2.3 * S)) ** 2)) * (1 - smoothstep(0.5, 1.0, d))
    hx = np.sqrt(np.clip(1 - ((xx - cx) / (rx*1.15)) ** 2, 0, 1))
    e['top'] = cy - ry * hx
    e['bot'] = cy + ry * hx * 0.85
    e['band'] = 1 - smoothstep(rx * 1.05, rx * 1.4, np.abs(xx - cx))

# Peau "sans oeil" : moyenne locale de la peau qui entoure l'oeil (convolution normalisée),
# pour que la paupière fermée ait la teinte de la peau voisine.
_w = np.ones((H, W), np.float32)
for e in EYES:
    cv2.ellipse(_w, (int(e['c'][0]*S), int(e['c'][1]*S)), (int(e['r'][0]*S*1.05), int(e['r'][1]*S*1.25)), 0, 0, 360, 0, -1)
_sig = 0.6 * EYES[1]['r'][0] * S
SKIN = cv2.GaussianBlur(base * _w[..., None], (0, 0), _sig) / np.maximum(cv2.GaussianBlur(_w, (0, 0), _sig), 1e-3)[..., None]
LID_TINT = np.array([0.9, 0.94, 1.0], np.float32)   # paupière légèrement rosée (BGR)
GRAIN = base - cv2.GaussianBlur(base, (0, 0), 1.2)
GRAIN = np.roll(GRAIN, -int(9 * S), axis=0)        # grain pris un peu au-dessus (front), pas sur l'oeil
for e in EYES:
    cx, cy = e['c'][0] * S, e['c'][1] * S
    d = ((xx - cx) / (e['r'][0]*S*1.6)) ** 2 + ((yy - cy) / (e['r'][1]*S*2.0)) ** 2
    e['cmask'] = 1 - smoothstep(0.25, 1.0, d)

def eye_pass(img, gaze_x, gaze_y, blinks):
    mx, my = xx.copy(), yy.copy()
    for e in EYES:
        w = e['iris']
        mx -= gaze_x * S * w
        my -= gaze_y * S * w
    out = cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    for e, b in zip(EYES, blinks):
        if b <= 0.01:
            continue
        cx, cy = e['c'][0] * S, e['c'][1] * S
        rx, ry = e['r'][0] * S, e['r'][1] * S
        top = e['top'] - 0.6 * S                      # contour supérieur de l'oeil
        # bord de la paupière fermée : arc incurvé vers le bas (plus bas au centre)
        hxe = np.sqrt(np.clip(1 - ((xx - cx) / (rx * 1.15)) ** 2, 0, 1))
        botc = cy + ry * (0.25 + (LID_END - 0.25) * hxe)
        lid = top + b * (botc - top)                  # bord actuel de la paupière
        # la paupière : la peau située au-dessus de l'oeil (sous l'arcade) est étirée vers le bas
        # jusqu'au bord de la paupière -> on garde la vraie texture de la peinture
        yA = top - 2.0 * S
        ys = np.where(yy < lid, yA + (yy - yA) * (top - yA) / np.maximum(lid - yA, 1e-3), yy)
        ys = np.where(yy < yA, yy, ys).astype(np.float32)
        lidimg = cv2.remap(img, xx, ys, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        tlid = np.clip((yy - top) / np.maximum(lid - top, 1e-3), 0, 1) * (yy < lid)
        shade = 1.0 - b * 0.12 * tlid ** 2
        # on adoucit les stries verticales dues à l'étirement, en mélangeant avec la peau voisine
        lidimg = 0.55 * cv2.GaussianBlur(lidimg, (0, 0), sigmaX=0.8 * S, sigmaY=0.25 * S) + 0.45 * SKIN
        lidimg = (lidimg + 0.9 * GRAIN) * shade[..., None]
        hx = 1 - smoothstep(0.3, 1.0, ((xx - cx) / (rx * 1.6)) ** 2)
        vy = smoothstep(yA - 1.5 * S, yA + 0.8 * S, yy) * (1 - smoothstep(lid + 0.2 * S, lid + 1.2 * S, yy))
        k = (hx * vy * smoothstep(0.0, 0.3, b))[..., None]
        out = out * (1 - k) + lidimg * k
        lash = np.exp(-((yy - lid) / (0.42 * S)) ** 2) * hxe ** 0.6 * smoothstep(0.15, 0.6, b)
        out = out * (1 - 0.5 * lash[..., None])
    return out

# ---------- head + breathing warp ----------
hc = (106 * S, 118 * S)
hd = ((xx - hc[0]) / (40 * S)) ** 2 + ((yy - hc[1]) / (60 * S)) ** 2
head_w = 1 - smoothstep(0.55, 1.35, hd)
pivot = (108 * S, 178 * S)
body_w = smoothstep(150 * S, 200 * S, yy)

def head_pass(img, dx, dy, ang, breath):
    a = np.deg2rad(ang)
    rx_ = xx - pivot[0]; ry_ = yy - pivot[1]
    # inverse rotation displacement
    ux = (np.cos(a) * rx_ + np.sin(a) * ry_ + pivot[0]) - xx
    uy = (-np.sin(a) * rx_ + np.cos(a) * ry_ + pivot[1]) - yy
    mx = xx + head_w * (ux - dx * S)
    my = yy + head_w * (uy - dy * S) + breath * S * body_w * smoothstep(329 * S, 190 * S, yy)
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ---------- timeline ----------
def ease(t):  # 0..1
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

BLINKS = [1.7, 5.4, 8.6, 9.0]   # incl. one double blink
WINK = 12.9                       # clin d'oeil (oeil droit de l'image = oeil gauche de Bolzano)
def blink_at(t):
    v = 0
    for t0 in BLINKS:
        u = t - t0
        if 0 <= u < 0.08: v = max(v, ease(u / 0.08))
        elif 0.08 <= u < 0.12: v = 1
        elif 0.12 <= u < 0.30: v = max(v, 1 - ease((u - 0.12) / 0.18))
    return v

def wink_at(t):
    u = t - WINK
    if u < 0: return 0.0
    if u < 0.16: return ease(u / 0.16)
    if u < 0.62: return 1.0
    if u < 0.95: return 1 - ease((u - 0.62) / 0.33)
    return 0.0

# gaze keyframes (orig px): (time, gx, gy) ; saccades of 0.12 s
GAZE = [(0, 0, 0), (2.6, -0.9, 0.15), (4.9, 0, 0), (7.2, 0.8, -0.2), (10.0, 0.15, 0.3),
        (11.8, 0, 0)]               # il regarde le spectateur avant le clin d'oeil
def gaze_at(t):
    gx = gy = 0
    for i, (t0, x, y) in enumerate(GAZE):
        if t >= t0:
            px, py = (GAZE[i - 1][1], GAZE[i - 1][2]) if i else (x, y)
            k = ease((t - t0) / 0.12)
            gx, gy = px + (x - px) * k, py + (y - py) * k
    return gx, gy

# head follows gaze slowly + gentle drift
def head_at(t, gx, gy_smooth):
    dx = 0.45 * gx_smooth_hist[int(t * FPS)] + 0.35 * np.sin(2 * np.pi * t / 11.3) + 0.15 * np.sin(2 * np.pi * t / 4.1)
    dy = 0.25 * np.sin(2 * np.pi * t / 7.7 + 1) + 0.25 * gy_smooth
    ang = 0.9 * np.sin(2 * np.pi * t / 13.7 + 0.5) + 0.35 * np.sin(2 * np.pi * t / 5.3) - 0.4 * gx_smooth_hist[int(t * FPS)]
    # complicité : la tête s'incline un peu vers l'oeil qui cligne
    w = ease((t - WINK + 0.35) / 0.4) * (1 - 0.4 * ease((t - WINK - 1.0) / 0.8))
    ang -= 2.2 * w
    dy -= 0.5 * w
    return dx, dy, ang

N = int(FPS * DUR)
g = np.array([gaze_at(i / FPS) for i in range(N)])
# slow follow (exponential smoothing ~0.8 s)
alpha = 1 - np.exp(-1 / (0.8 * FPS))
gs = np.zeros_like(g)
for i in range(N):
    gs[i] = g[i] if i == 0 else gs[i - 1] + alpha * (g[i] - gs[i - 1])
gx_smooth_hist = gs[:, 0]

def frame(i):
    t = i / FPS
    gx, gy = g[i]
    b = blink_at(t)
    wk = wink_at(t)
    img = eye_pass(base, gx, gy, [max(b, 0.18 * wk), max(b, wk)])
    dx, dy, ang = head_at(t, gx, gs[i, 1])
    breath = 0.55 * np.sin(2 * np.pi * t / 4.6)
    img = head_pass(img, dx, dy, ang, breath)
    return np.clip(img, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    mode = sys.argv[2]
    if mode == 'preview':
        for t in sys.argv[3:]:
            cv2.imwrite(f'prev_{t}.png', frame(int(float(t) * FPS)))
    else:
        out = sys.argv[3]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                              '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                              '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
        for i in range(N):
            p.stdin.write(frame(i).tobytes())
        p.stdin.close(); sys.exit(p.wait())
