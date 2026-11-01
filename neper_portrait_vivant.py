import sys, subprocess, numpy as np, cv2

S = 3.6                      # orig 400x300 -> 1440x1080
W, H = 1440, 1080
FPS, DUR = 30, 30.0
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
EYES = [dict(c=(210.6, 95.2), r=(7.0, 4.2)), dict(c=(232.8, 95.0), r=(7.2, 4.2))]
for e in EYES:
    cx, cy = e['c'][0] * S, e['c'][1] * S
    rx, ry = e['r'][0] * S, e['r'][1] * S
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    e['mask'] = 1 - smoothstep(1.25, 2.1, d)                    # feathered eye area
    e['iris'] = np.exp(-(((xx - cx) / (3.2 * S)) ** 2 + ((yy - cy) / (3.0 * S)) ** 2)) * (1 - smoothstep(0.5, 1.0, d))
    hx = np.sqrt(np.clip(1 - ((xx - cx) / (rx*1.15)) ** 2, 0, 1))
    e['top'] = cy - ry * hx
    e['bot'] = cy + ry * hx * 0.85
    e['band'] = 1 - smoothstep(rx * 1.05, rx * 1.4, np.abs(xx - cx))

_m = np.zeros((H, W), np.uint8)
for e in EYES:
    cv2.ellipse(_m, (int(e['c'][0]*S), int(e['c'][1]*S)), (int(e['r'][0]*S*1.45), int(e['r'][1]*S*1.6)), 0, 0, 360, 255, -1)
SKIN = cv2.inpaint(np.clip(base,0,255).astype(np.uint8), _m, 9, cv2.INPAINT_TELEA)
SKIN = cv2.GaussianBlur(SKIN, (0, 0), 3).astype(np.float32)
SKIN = np.where(_m[..., None] > 0, SKIN, base)
for e in EYES:
    cx, cy = e['c'][0] * S, e['c'][1] * S
    d = ((xx - cx) / (e['r'][0]*S*1.25)) ** 2 + ((yy - cy) / (e['r'][1]*S*1.45)) ** 2
    e['cmask'] = 1 - smoothstep(0.45, 1.05, d)

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
        top = e['top'] - 0.6 * S                      # upper eye contour
        span = (e['c'][1] + 0.45 * e['r'][1]) * S - top
        lid = top + b * span                          # current lid edge
        yA = top - 2.2 * S                            # skin above that gets stretched
        ys = np.where(yy < lid, yA + (yy - yA) * (top - yA) / np.maximum(lid - yA, 1e-3), yy)
        ys = np.where(yy < yA, yy, ys).astype(np.float32)
        hx = 1 - smoothstep(0.35, 1.0, ((xx - e['c'][0] * S) / (e['r'][0] * S * 1.4)) ** 2)
        vy = smoothstep(yA - 2.5 * S, yA + 0.5 * S, yy) * (1 - smoothstep(e['bot'] + 1.0 * S, e['bot'] + 3 * S, yy))
        k = (hx * vy)[..., None]
        lidimg = cv2.remap(img, xx, ys, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        sm = cv2.GaussianBlur(lidimg, (0, 0), sigmaX=2.2 * S, sigmaY=0.6 * S)
        above = (1 - smoothstep(lid - 1.0 * S, lid - 0.2 * S, yy))[..., None] * b
        lidimg = lidimg * (1 - above) + sm * above
        lash = np.exp(-((yy - lid) / (0.45 * S)) ** 2) * hx * min(1.0, b * 1.4)
        lidimg = lidimg * (1 - 0.35 * lash[..., None])
        # lower part of the eye still visible below the lid
        out = out * (1 - k) + lidimg * k
    return out

# ---------- head + breathing warp ----------
hc = (223 * S, 102 * S)
hd = ((xx - hc[0]) / (40 * S)) ** 2 + ((yy - hc[1]) / (58 * S)) ** 2
head_w = 1 - smoothstep(0.55, 1.35, hd)
pivot = (226 * S, 150 * S)
body_w = smoothstep(100 * S, 135 * S, xx) * smoothstep(70 * S, 125 * S, yy) * (1 - smoothstep(380 * S, 400 * S, xx))

def head_pass(img, dx, dy, ang, breath):
    a = np.deg2rad(ang)
    rx_ = xx - pivot[0]; ry_ = yy - pivot[1]
    # inverse rotation displacement
    ux = (np.cos(a) * rx_ + np.sin(a) * ry_ + pivot[0]) - xx
    uy = (-np.sin(a) * rx_ + np.cos(a) * ry_ + pivot[1]) - yy
    mx = xx + head_w * (ux - dx * S)
    my = yy + head_w * (uy - dy * S) + breath * S * body_w * smoothstep(300 * S, 120 * S, yy)
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ---------- timeline ----------
def ease(t):  # 0..1
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

BLINKS = [1.6, 5.2, 8.9, 9.3, 13.4, 17.0, 20.8, 24.6, 27.9]   # incl. one double blink
def blink_at(t):
    v = 0
    for t0 in BLINKS:
        u = t - t0
        if 0 <= u < 0.08: v = max(v, ease(u / 0.08))
        elif 0.08 <= u < 0.12: v = 1
        elif 0.12 <= u < 0.30: v = max(v, 1 - ease((u - 0.12) / 0.18))
    return v

# gaze keyframes (orig px): (time, gx, gy) ; saccades of 0.12 s
GAZE = [(0, 0, 0), (3.5, -1.3, 0.2), (6.8, 0, 0), (11.0, 1.1, -0.3), (14.5, 0.2, 0.4),
        (18.5, -1.0, 0.5), (21.5, 0, 0), (25.5, 0.9, 0), (28.2, 0, 0)]
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
    img = eye_pass(base, gx, gy, [b, b])
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
