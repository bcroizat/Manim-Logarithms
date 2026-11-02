"""
Bolzano et Weierstrass, portraits vivants côte à côte (15 s) :
mouvements des yeux / de la tête / respiration, puis ils se regardent
et se font un clin d'oeil en même temps.

Usage :
    python bolzano_weierstrass_portraits.py bolzano.jpg weierstrass.jpg render Bolzano_Weierstrass.mp4
    python bolzano_weierstrass_portraits.py bolzano.jpg weierstrass.jpg preview 5.0 13.2
"""
import sys, subprocess
import numpy as np, cv2

W, H = 1920, 1080
FPS, DUR = 30, 15.0
N = int(FPS * DUR)
BG = (22, 20, 18)                 # fond (BGR)
MIRROR_WEIERSTRASS = True         # retourne Weierstrass pour qu'il regarde vers Bolzano
TURN_T = 10.2                     # ils se tournent l'un vers l'autre
WINK_T = 12.9                     # clin d'oeil simultané


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def ease(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


class Portrait:
    """Un tableau animé. Toutes les coordonnées sont celles de l'image d'origine (px)."""

    def __init__(self, img, eyes, head_c, head_r, pivot, body_y, iris_r, lid_end=1.3,
                 lid_mix=0.55, lid_gain=(1.0, 1.0, 1.0)):
        h0 = img.shape[0]
        S = self.S = H / h0
        self.w = int(round(img.shape[1] * S / 2) * 2)
        self.h = H
        base = cv2.resize(img, (self.w, self.h), interpolation=cv2.INTER_LANCZOS4)
        blur = cv2.GaussianBlur(base, (0, 0), 2.0)
        base = cv2.addWeighted(base, 1.35, blur, -0.35, 0).astype(np.float32)
        self.base = base
        xx, yy = np.meshgrid(np.arange(self.w, dtype=np.float32), np.arange(self.h, dtype=np.float32))
        self.xx, self.yy = xx, yy
        self.lid_end = lid_end
        self.lid_mix = lid_mix                                   # part de peau étirée (le reste : peau voisine)
        self.lid_gain = np.array(lid_gain, np.float32)          # teinte de la paupière (BGR)

        self.eyes = []
        for (c, r) in eyes:
            cx, cy = c[0] * S, c[1] * S
            rx, ry = r[0] * S, r[1] * S
            d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
            e = dict(cx=cx, cy=cy, rx=rx, ry=ry)
            e['iris'] = np.exp(-(((xx - cx) / (iris_r * S)) ** 2 + ((yy - cy) / (iris_r * S)) ** 2)) \
                * (1 - smoothstep(0.5, 1.0, d))
            hx = np.sqrt(np.clip(1 - ((xx - cx) / (rx * 1.15)) ** 2, 0, 1))
            e['top'] = cy - ry * hx
            e['hxe'] = hx
            self.eyes.append(e)

        # peau "sans oeil" : moyenne locale de la peau autour de l'oeil (convolution normalisée)
        wgt = np.ones((self.h, self.w), np.float32)
        for e in self.eyes:
            cv2.ellipse(wgt, (int(e['cx']), int(e['cy'])), (int(e['rx'] * 1.05), int(e['ry'] * 1.25)),
                        0, 0, 360, 0, -1)
        sig = 0.6 * max(e['rx'] for e in self.eyes)
        self.skin = cv2.GaussianBlur(base * wgt[..., None], (0, 0), sig) \
            / np.maximum(cv2.GaussianBlur(wgt, (0, 0), sig), 1e-3)[..., None]
        grain = base - cv2.GaussianBlur(base, (0, 0), 1.2)
        self.grain = np.roll(grain, -int(9 * S), axis=0)

        # tête + respiration
        hc = (head_c[0] * S, head_c[1] * S)
        hd = ((xx - hc[0]) / (head_r[0] * S)) ** 2 + ((yy - hc[1]) / (head_r[1] * S)) ** 2
        self.head_w = 1 - smoothstep(0.55, 1.35, hd)
        self.pivot = (pivot[0] * S, pivot[1] * S)
        self.body_w = smoothstep(body_y * S, (body_y + 40) * S, yy) * smoothstep(self.h, (body_y + 15) * S, yy)

    # ------------------------------------------------------------------ yeux
    def eye_pass(self, gx, gy, blinks):
        S, xx, yy = self.S, self.xx, self.yy
        mx, my = xx.copy(), yy.copy()
        for e in self.eyes:
            mx -= gx * S * e['iris']
            my -= gy * S * e['iris']
        img = self.base
        out = cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        for e, b in zip(self.eyes, blinks):
            if b <= 0.01:
                continue
            cx, cy, rx, ry, hxe = e['cx'], e['cy'], e['rx'], e['ry'], e['hxe']
            top = e['top'] - 0.6 * S
            botc = cy + ry * (0.25 + (self.lid_end - 0.25) * hxe)    # paupière fermée : arc vers le bas
            lid = top + b * (botc - top)
            # la peau sous l'arcade est étirée vers le bas jusqu'au bord de la paupière
            yA = top - 2.0 * S
            ys = np.where(yy < lid, yA + (yy - yA) * (top - yA) / np.maximum(lid - yA, 1e-3), yy)
            ys = np.where(yy < yA, yy, ys).astype(np.float32)
            lidimg = cv2.remap(img, xx, ys, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            tlid = np.clip((yy - top) / np.maximum(lid - top, 1e-3), 0, 1) * (yy < lid)
            shade = 1.0 - b * 0.12 * tlid ** 2
            m = self.lid_mix
            lidimg = m * cv2.GaussianBlur(lidimg, (0, 0), sigmaX=0.8 * S, sigmaY=0.25 * S) + (1 - m) * self.skin
            lidimg = (lidimg + 0.9 * self.grain) * shade[..., None] * self.lid_gain
            hx = 1 - smoothstep(0.3, 1.0, ((xx - cx) / (rx * 1.6)) ** 2)
            vy = smoothstep(yA - 1.5 * S, yA + 0.8 * S, yy) * (1 - smoothstep(lid + 0.2 * S, lid + 1.2 * S, yy))
            k = (hx * vy * smoothstep(0.0, 0.3, b))[..., None]
            out = out * (1 - k) + lidimg * k
            lash = np.exp(-((yy - lid) / (0.42 * S)) ** 2) * hxe ** 0.6 * smoothstep(0.15, 0.6, b)
            out = out * (1 - 0.5 * lash[..., None])
        return out

    # ----------------------------------------------------------------- tête
    def head_pass(self, img, dx, dy, ang, breath):
        S, xx, yy = self.S, self.xx, self.yy
        a = np.deg2rad(ang)
        rx_, ry_ = xx - self.pivot[0], yy - self.pivot[1]
        ux = (np.cos(a) * rx_ + np.sin(a) * ry_ + self.pivot[0]) - xx
        uy = (-np.sin(a) * rx_ + np.cos(a) * ry_ + self.pivot[1]) - yy
        mx = xx + self.head_w * (ux - dx * S)
        my = yy + self.head_w * (uy - dy * S) + breath * S * self.body_w
        return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REFLECT)


class Timeline:
    """Mouvements d'un personnage. toward = +1 si l'autre est à droite, -1 s'il est à gauche."""

    def __init__(self, blinks, gaze, toward, wink_eye, phase, gaze_amp=1.0):
        self.blinks, self.toward, self.wink_eye, self.phase = blinks, toward, wink_eye, phase
        g = np.array([self._gaze(gaze, i / FPS) for i in range(N)]) * gaze_amp
        alpha = 1 - np.exp(-1 / (0.8 * FPS))                    # la tête suit le regard (~0,8 s)
        gs = np.zeros_like(g)
        for i in range(N):
            gs[i] = g[i] if i == 0 else gs[i - 1] + alpha * (g[i] - gs[i - 1])
        self.g, self.gs = g, gs

    @staticmethod
    def _gaze(keys, t):
        gx = gy = 0
        for i, (t0, x, y) in enumerate(keys):
            if t >= t0:
                px, py = (keys[i - 1][1], keys[i - 1][2]) if i else (x, y)
                k = ease((t - t0) / 0.12)                       # saccade de 0,12 s
                gx, gy = px + (x - px) * k, py + (y - py) * k
        return gx, gy

    def blink(self, t):
        v = 0
        for t0 in self.blinks:
            u = t - t0
            if 0 <= u < 0.08: v = max(v, ease(u / 0.08))
            elif 0.08 <= u < 0.12: v = 1
            elif 0.12 <= u < 0.30: v = max(v, 1 - ease((u - 0.12) / 0.18))
        return v

    @staticmethod
    def wink(t):
        u = t - WINK_T
        if u < 0: return 0.0
        if u < 0.16: return ease(u / 0.16)
        if u < 0.62: return 1.0
        if u < 0.95: return 1 - ease((u - 0.62) / 0.33)
        return 0.0

    def head(self, i):
        t, p = i / FPS, self.phase
        gx = self.gs[i, 0]
        dx = 0.45 * gx + 0.35 * np.sin(2 * np.pi * t / 11.3 + p) + 0.15 * np.sin(2 * np.pi * t / 4.1 + 2 * p)
        dy = 0.25 * np.sin(2 * np.pi * t / 7.7 + 1 + p) + 0.25 * self.gs[i, 1]
        ang = 0.9 * np.sin(2 * np.pi * t / 13.7 + 0.5 + p) + 0.35 * np.sin(2 * np.pi * t / 5.3 + p) - 0.4 * gx
        # ils se tournent l'un vers l'autre
        turn = ease((t - TURN_T) / 1.2)
        dx += 1.2 * self.toward * turn
        ang -= 1.3 * self.toward * turn
        # complicité : la tête s'incline un peu au moment du clin d'oeil
        w = ease((t - WINK_T + 0.35) / 0.4) * (1 - 0.4 * ease((t - WINK_T - 1.0) / 0.8))
        ang -= 2.0 * self.toward * w
        dy -= 0.5 * w
        return dx, dy, ang

    def lids(self, t):
        b, wk = self.blink(t), self.wink(t)
        out = [max(b, 0.18 * wk), max(b, 0.18 * wk)]
        out[self.wink_eye] = max(b, wk)
        return out


def build(bolzano_path, weier_path):
    # --- Bolzano (250x329) : il est à droite, il regarde vers la gauche
    bz = Portrait(cv2.imread(bolzano_path),
                  eyes=[((85.8, 118.5), (4.6, 2.9)), ((118.8, 118.3), (5.4, 3.0))],
                  head_c=(106, 118), head_r=(40, 60), pivot=(108, 178), body_y=150, iris_r=2.4)
    bz_t = Timeline(blinks=[1.7, 5.4, 8.6, 9.0],
                    gaze=[(0, 0, 0), (2.6, -0.9, 0.15), (4.9, 0, 0), (7.2, 0.8, -0.2), (9.4, 0.15, 0.3),
                          (TURN_T, -1.1, 0.1)],
                    toward=-1, wink_eye=0, phase=0.0)

    # --- Weierstrass (265x326) : il est à gauche ; image retournée pour qu'il regarde vers la droite
    wimg = cv2.imread(weier_path)
    ww = wimg.shape[1]
    mx = (lambda x: ww - 1 - x) if MIRROR_WEIERSTRASS else (lambda x: x)
    if MIRROR_WEIERSTRASS:
        wimg = cv2.flip(wimg, 1)
    eyes_w = sorted([((mx(143.2), 50.9), (5.3, 2.2)), ((mx(168.6), 51.2), (5.5, 2.2))], key=lambda e: e[0][0])
    wz = Portrait(wimg, eyes=eyes_w, head_c=(mx(157), 50), head_r=(42, 50), pivot=(mx(160), 100),
                  body_y=95, iris_r=2.0, lid_end=1.25,
                  lid_mix=0.3, lid_gain=(0.68, 0.7, 0.84))     # sourcils blancs : paupière plus sombre et rosée
    toward_w = 1
    wz_t = Timeline(blinks=[0.9, 3.8, 7.3, 11.2],
                    gaze=[(0, 0, 0), (1.9, 0.7, 0.2), (4.4, -0.6, 0.0), (6.6, 0, 0.3), (8.8, -0.4, -0.1),
                          (TURN_T + 0.15, 1.1 * toward_w, 0.1)],
                    toward=toward_w, wink_eye=1, phase=1.7, gaze_amp=0.8)
    return (wz, wz_t), (bz, bz_t)


def compose(left, right, i):
    t = i / FPS
    canvas = np.empty((H, W, 3), np.float32)
    canvas[:] = BG
    gap = 24
    total = left[0].w + right[0].w + gap
    x0 = (W - total) // 2
    for (p, tl), x in ((left, x0), (right, x0 + left[0].w + gap)):
        gx, gy = tl.g[i]
        img = p.eye_pass(gx, gy, tl.lids(t))
        dx, dy, ang = tl.head(i)
        breath = 0.55 * np.sin(2 * np.pi * t / 4.6 + tl.phase)
        img = p.head_pass(img, dx, dy, ang, breath)
        canvas[:, x:x + p.w] = img
    return np.clip(canvas, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    left, right = build(sys.argv[1], sys.argv[2])
    mode = sys.argv[3]
    if mode == 'preview':
        for t in sys.argv[4:]:
            cv2.imwrite(f'prev2_{t}.png', compose(left, right, int(float(t) * FPS)))
    else:
        out = sys.argv[4]
        proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                                 '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
                                stdin=subprocess.PIPE)
        for i in range(N):
            proc.stdin.write(compose(left, right, i).tobytes())
        proc.stdin.close()
        sys.exit(proc.wait())
