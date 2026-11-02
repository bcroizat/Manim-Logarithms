"""
Construction de la borne supérieure par dichotomie
Manim Community Edition (testé pour la syntaxe de la v0.18 / v0.19)

Rendu :
    manim -pqh borne_superieure.py BorneSuperieure      # 1080p 60 i/s
    manim -pql borne_superieure.py BorneSuperieure      # aperçu rapide 480p
"""
from manim import *
import numpy as np

# ----------------------------------------------------------------- couleurs
BG = "#0d1117"
COL_AXIS = "#9aa4b2"
COL_TXT = "#e6edf3"
COL_A = "#4fa3ff"      # éléments de A
COL_D = "#3ddc97"      # D : n'est pas un majorant
COL_K = "#ff8a3d"      # K : majorant
COL_M = "#ffd43b"      # milieu M
COL_NO = "#ff5c7a"     # témoin "M n'est pas un majorant"
COL_SUP = "#f7c948"    # sup(A)

# ----------------------------------------------------------------- données
S = 6.4                # sup(A) (non atteint : les points s'accumulent à gauche de S)
D0, K0 = 3.2, 9.0      # départ : D au milieu de A, K majorant bien au-dessus de sup(A)
N_STEPS = 16
LAST_ZOOM_STEP = 9     # après cette étape on ne zoome plus : on regarde D et K se rapprocher
VIEW0 = (-0.5, 10.5)   # fenêtre initiale sur la droite réelle
X0, X1 = -6.3, 6.3     # étendue de l'axe à l'écran
AY = -0.35             # ordonnée de l'axe à l'écran


def nice_step(span, target=7):
    raw = span / target
    mag = 10 ** np.floor(np.log10(raw))
    for m in (1, 2, 5, 10):
        if m * mag >= raw * (1 - 1e-9):
            return m * mag
    return 10 * mag


def fr_num(x, dec):
    """Nombre au format français pour Text (virgule décimale, vrai signe moins)."""
    return f"{x:.{dec}f}".replace(".", ",").replace("-", "−")


def tex_num(x, dec):
    """Nombre au format français pour MathTex."""
    return f"{x:.{dec}f}".replace(".", "{,}")


def fr(s, size=30, color=COL_TXT, **kw):
    return Text(s, font_size=size, color=color, **kw)


class BorneSuperieure(Scene):
    # ============================================================ utilitaires
    def sx(self, x):
        lo, hi = self.lo.get_value(), self.hi.get_value()
        return X0 + (X1 - X0) * (x - lo) / (hi - lo)

    @staticmethod
    def clipx(X):
        return min(max(X, X0 - 0.3), X1 + 0.3)

    def zoom_to(self, nlo, nhi, run_time=2.0):
        """Zoom géométrique (vitesse de zoom constante) vers la fenêtre [nlo, nhi]."""
        lo0, hi0 = self.lo.get_value(), self.hi.get_value()
        c0, s0 = (lo0 + hi0) / 2, hi0 - lo0
        c1, s1 = (nlo + nhi) / 2, nhi - nlo

        def upd(mob, alpha):
            a = smooth(alpha)
            s = s0 * (s1 / s0) ** a
            if abs(s0 - s1) > 1e-12:
                c = c0 + (c1 - c0) * (s0 - s) / (s0 - s1)
            else:
                c = c0 + (c1 - c0) * a
            self.lo.set_value(c - s / 2)
            self.hi.set_value(c + s / 2)

        self.play(UpdateFromAlphaFunc(self.lo, upd), run_time=run_time, rate_func=linear)

    # ------------------------------------------------------------- dessins
    def make_axis(self):
        lo, hi = self.lo.get_value(), self.hi.get_value()
        g = VGroup(
            Arrow([X0 - 0.45, AY, 0], [X1 + 0.6, AY, 0], buff=0, color=COL_AXIS,
                  stroke_width=3, max_tip_length_to_length_ratio=0.02)
        )
        step = nice_step(hi - lo)
        dec = max(0, int(-np.floor(np.log10(step) + 1e-9)))
        for i in range(int(np.ceil(lo / step)), int(np.floor(hi / step)) + 1):
            v = i * step
            x = self.sx(v)
            if X0 - 0.05 <= x <= X1 + 0.05:
                g.add(Line([x, AY - 0.1, 0], [x, AY + 0.1, 0], color=COL_AXIS, stroke_width=2))
                g.add(fr(fr_num(v, dec), 18, COL_AXIS).move_to([x, AY - 0.4, 0]))
        return g

    def make_dots(self):
        lo, hi = self.lo.get_value(), self.hi.get_value()
        mg = 0.01 * (hi - lo)
        return VGroup(*[
            Dot([self.sx(a), AY, 0], radius=0.075, color=COL_A)
            for a in self.A if lo - mg <= a <= hi + mg
        ])

    def make_zones(self):
        op = self.zone_op.get_value()
        xd = self.clipx(self.sx(self.d.get_value()))
        xk = self.clipx(self.sx(self.k.get_value()))
        h = 0.55

        def band(a, b, col, o):
            b = max(b, a + 1e-3)
            return Polygon([a, AY - h, 0], [b, AY - h, 0], [b, AY + h, 0], [a, AY + h, 0],
                           stroke_width=0, fill_color=col, fill_opacity=o * op)

        return VGroup(band(X0 - 0.3, xd, COL_D, 0.13),
                      band(xd, xk, COL_M, 0.09),
                      band(xk, X1 + 0.3, COL_K, 0.13))

    def make_trails(self):
        """Petites marques aux anciennes positions de D et K."""
        g = VGroup()
        lo, hi = self.lo.get_value(), self.hi.get_value()
        for v, col in [(v, COL_D) for v in self.hist_d] + [(v, COL_K) for v in self.hist_k]:
            if lo <= v <= hi:
                x = self.sx(v)
                g.add(Line([x, AY + 0.12, 0], [x, AY + 0.32, 0], color=col,
                           stroke_width=3, stroke_opacity=0.45))
        return g

    def make_marker(self, tracker, name, color, side=0):
        """side = -1 (D) / +1 (K) : l'étiquette s'écarte quand D et K sont proches ;
        side = 0 (M) : l'étiquette monte d'un cran quand D et K sont proches."""
        stem = Line(UP * 0.27, DOWN * 0.27, color=color, stroke_width=5)
        tri = Triangle(fill_color=color, fill_opacity=1, stroke_width=0).scale(0.13).rotate(PI)
        lab = MathTex(name, color=color).scale(0.85)
        grp = VGroup(stem, tri, lab)

        def upd(_):
            x = self.sx(tracker.get_value())
            xd, xk = self.sx(self.d.get_value()), self.sx(self.k.get_value())
            mid = (xd + xk) / 2
            lx, ly = x, AY + 0.8
            if side < 0:
                lx = min(x, mid - 0.3)
            elif side > 0:
                lx = max(x, mid + 0.3)
            elif xk - xd < 1.4:
                ly = AY + 1.2
            stem.move_to([x, AY, 0])
            tri.move_to([x, AY + 0.42, 0])
            lab.move_to([lx, ly, 0])

        upd(grp)
        grp.add_updater(upd)
        return grp

    def make_table(self, n):
        d, k = self.d.get_value(), self.k.get_value()
        t = VGroup(
            MathTex(rf"D_{{{n}}} = {tex_num(d, 5)}", color=COL_D),
            MathTex(rf"K_{{{n}}} = {tex_num(k, 5)}", color=COL_K),
            MathTex(rf"K_{{{n}}}-D_{{{n}}} = {tex_num(k - d, 5)}", color=COL_M),
        ).scale(0.6).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        return t.to_corner(UR, buff=0.4)

    def step_label(self, n):
        return fr(f"Étape {n}", 32, COL_TXT, weight=BOLD).to_corner(UL, buff=0.4)

    # ============================================================== scène
    def construct(self):
        self.camera.background_color = BG
        rng = np.random.default_rng(3)
        bulk = rng.uniform(0.7, 5.3, 14)
        cluster = S - 0.9 * 0.55 ** np.arange(0, 48)   # s'accumule vers S sans l'atteindre
        self.A = np.sort(np.concatenate([bulk, cluster]))

        self.lo = ValueTracker(VIEW0[0])
        self.hi = ValueTracker(VIEW0[1])
        self.d = ValueTracker(D0)
        self.k = ValueTracker(K0)
        self.m_tr = ValueTracker(D0)
        self.zone_op = ValueTracker(0)
        self.hist_d, self.hist_k = [], []
        self.D_seq = [D0]      # D_0, D_1, D_2, ... (valeurs de D après chaque étape)

        self.intro_title()
        self.present_set()
        self.present_DK()
        self.run_steps()
        self.conclusion()

    # ------------------------------------------------------------- titre
    def intro_title(self):
        title = fr("Construction de la borne supérieure", 50, weight=BOLD)
        title.set_color_by_gradient(COL_A, COL_SUP)
        sub = fr("par dichotomie", 32, GREY_B).next_to(title, DOWN, buff=0.4)
        bar = Line(LEFT * 4, RIGHT * 4, color=COL_SUP, stroke_width=2).next_to(sub, DOWN, buff=0.35)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(sub, shift=UP * 0.3), Create(bar))
        self.wait(1.5)
        self.play(FadeOut(VGroup(title, sub, bar), shift=UP * 0.5))

    # ---------------------------------------------------------- ensemble A
    def present_set(self):
        self.axis = always_redraw(self.make_axis)
        self.play(FadeIn(self.axis), run_time=1)

        static = self.make_dots()
        self.play(LaggedStart(*[GrowFromCenter(d) for d in static], lag_ratio=0.06), run_time=2.5)
        # IMPORTANT : LaggedStart ajoute à la scène un groupe contenant ces points ;
        # il faut retirer chaque point individuellement, sinon une copie figée
        # resterait affichée et ne suivrait pas les zooms.
        self.remove(static, *static)
        self.dots = always_redraw(self.make_dots)
        self.add(self.dots)

        labA = MathTex("A", color=COL_A).scale(1.3).move_to([self.sx(2.8), AY + 0.9, 0])
        t1 = fr("A : une partie de ℝ, non vide et majorée", 32).move_to(DOWN * 2.0)
        self.play(Write(labA), FadeIn(t1, shift=UP * 0.2))
        self.wait(1)

        note = fr("les éléments de A s'accumulent ici", 22, GREY_B).move_to([self.sx(7.8), AY + 1.5, 0])
        arr = Arrow(note.get_bottom() + LEFT * 0.4, [self.sx(6.25), AY + 0.15, 0], buff=0.08,
                    color=GREY_B, stroke_width=2, max_tip_length_to_length_ratio=0.15)
        self.play(FadeIn(note), GrowArrow(arr))
        self.wait(1.5)
        self.play(FadeOut(VGroup(labA, t1, note, arr)))

    # --------------------------------------------------------- D, K, zones
    def present_DK(self):
        self.K = self.make_marker(self.k, "K", COL_K, side=1)
        tK = fr("K : un majorant de A", 32, COL_K).move_to(DOWN * 1.9)
        sK = fr("tout élément de A est inférieur ou égal à K", 24, GREY_B).next_to(tK, DOWN, buff=0.2)
        self.play(FadeIn(self.K, shift=DOWN * 0.4), FadeIn(tK))
        self.play(FadeIn(sK))
        self.wait(1.5)

        self.D = self.make_marker(self.d, "D", COL_D, side=-1)
        tD = fr("D : un réel qui n'est pas un majorant de A", 32, COL_D).move_to(DOWN * 1.9)
        sD = fr("au moins un élément de A est strictement plus grand que D", 24, GREY_B) \
            .next_to(tD, DOWN, buff=0.2)
        self.play(FadeOut(VGroup(tK, sK)), FadeIn(self.D, shift=DOWN * 0.4), FadeIn(tD))
        self.play(FadeIn(sD))
        self.wait(1.5)
        self.play(FadeOut(VGroup(tD, sD)))

        # zones colorées
        self.zones = always_redraw(self.make_zones)
        self.trails = always_redraw(self.make_trails)
        self.add(self.zones, self.trails)
        self.bring_to_back(self.zones)
        self.play(self.zone_op.animate.set_value(1), run_time=1.2)

        xd, xk = self.sx(D0), self.sx(K0)
        ya, yl = AY + 1.3, AY + 1.68

        def darrow(a, b, col):
            return DoubleArrow([a, ya, 0], [b, ya, 0], buff=0, color=col, stroke_width=4,
                               tip_length=0.18, max_tip_length_to_length_ratio=0.5)

        al = darrow(X0, xd - 0.12, COL_D)
        am = darrow(xd + 0.12, xk - 0.12, COL_M)
        ar = darrow(xk + 0.12, X1 + 0.3, COL_K)
        zl = fr("pas des majorants", 22, COL_D).move_to([(X0 + xd) / 2, yl, 0])
        zm = fr("on ne sait pas encore", 22, COL_M).move_to([(xd + xk) / 2, yl, 0])
        zr = fr("majorants", 22, COL_K).move_to([(xk + X1 + 0.3) / 2, yl, 0])
        self.play(LaggedStart(AnimationGroup(GrowFromCenter(al), FadeIn(zl)),
                              AnimationGroup(GrowFromCenter(ar), FadeIn(zr)),
                              AnimationGroup(GrowFromCenter(am), FadeIn(zm)), lag_ratio=0.5),
                  run_time=2.2)
        why1 = fr("un réel plus petit que D ne majore pas A", 24, COL_D)
        why2 = fr("un réel plus grand que K majore A", 24, COL_K)
        why = VGroup(why1, why2).arrange(DOWN, buff=0.2).move_to(DOWN * 2.1)
        self.play(FadeIn(why1))
        self.wait(1)
        self.play(FadeIn(why2))
        self.wait(2.5)
        self.play(FadeOut(VGroup(al, am, ar, zl, zm, zr, why)))

        # règle de l'algorithme
        r1 = MathTex(r"M=\frac{D+K}{2}", color=COL_M).scale(0.8)
        r2 = VGroup(fr("si M majore A", 24, COL_K), MathTex(r"\Rightarrow", color=COL_TXT).scale(0.7),
                    fr("K ← M", 24, COL_K)).arrange(RIGHT, buff=0.2)
        r3 = VGroup(fr("sinon", 24, COL_D), MathTex(r"\Rightarrow", color=COL_TXT).scale(0.7),
                    fr("D ← M", 24, COL_D)).arrange(RIGHT, buff=0.2)
        rule = VGroup(r1, r2, r3).arrange(DOWN, buff=0.18)
        box = SurroundingRectangle(rule, color=GREY_B, buff=0.22, corner_radius=0.12, stroke_width=1.5)
        self.rule = VGroup(box, rule)
        head = fr("L'algorithme", 34, COL_TXT, weight=BOLD)
        big = VGroup(head, self.rule.copy()).arrange(DOWN, buff=0.25).scale(1.08)
        big.to_edge(UP, buff=0.15)   # au-dessus de la droite des nombres
        self.play(FadeIn(big, shift=DOWN * 0.3))
        self.wait(3)
        self.rule.move_to(UP * 2.75)
        self.play(FadeOut(big[0]), ReplacementTransform(big[1], self.rule))

        self.table = self.make_table(0)
        self.slab = self.step_label(0)
        self.play(FadeIn(self.table), FadeIn(self.slab))
        self.wait(1)

    # -------------------------------------------------------------- étapes
    def run_steps(self):
        self.frozen = False
        for n in range(1, LAST_ZOOM_STEP + 1):
            level = 0 if n <= 3 else (1 if n <= 7 else 2)
            self.do_step(n, level)
            if n < LAST_ZOOM_STEP:
                self.maybe_zoom(level)
        self.final_zoom()

        # Plus de zoom : on observe D et K se rapprocher, et on note ce que l'on constate.
        self.frozen = True
        obs = self.make_observations()
        for i, n in enumerate(range(LAST_ZOOM_STEP + 1, N_STEPS + 1)):
            self.do_step(n, 2)
            if i < len(obs):
                self.play(FadeIn(obs[i], shift=UP * 0.15), run_time=0.8)
                self.wait(1.2)
        self.obs = obs
        self.wait(1.5)

    def final_zoom(self):
        d, k = self.d.get_value(), self.k.get_value()
        c, span = (d + k) / 2, 1.25 * (k - d)
        lo, hi = self.lo.get_value(), self.hi.get_value()
        badge = fr(f"zoom ×{(hi - lo) / span:.0f}", 24, GREY_B).next_to(self.slab, DOWN, aligned_edge=LEFT)
        self.play(FadeIn(badge), run_time=0.3)
        self.zoom_to(c - span / 2, c + span / 2, run_time=1.5)
        self.play(FadeOut(badge), run_time=0.3)
        t = fr("Désormais on ne zoome plus : regardons D et K", 30).move_to(DOWN * 2.0)
        self.play(FadeIn(t))
        self.wait(2)
        self.play(FadeOut(t))

    def make_observations(self):
        sz = 26
        o1 = VGroup(MathTex(r"(D_n)", color=COL_D), fr("est croissante", sz)).arrange(RIGHT, buff=0.18)
        o2 = VGroup(MathTex(r"(K_n)", color=COL_K), fr("est décroissante", sz)).arrange(RIGHT, buff=0.18)
        o3 = VGroup(MathTex(r"D_n<K_n"), fr("à chaque étape", sz)).arrange(RIGHT, buff=0.18)
        o4 = VGroup(fr("la distance est divisée par 2 à chaque étape :", sz),
                    MathTex(r"K_n-D_n=\frac{K_0-D_0}{2^n}\xrightarrow[n\to+\infty]{}0", color=COL_M)
                    ).arrange(RIGHT, buff=0.2)
        obs = VGroup(o1, o2, o3, o4)
        for o in obs:
            o.scale(0.8)
        obs.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        obs.next_to([0, AY - 0.95, 0], DOWN, buff=0)
        return obs

    def do_step(self, n, level):
        d, k = self.d.get_value(), self.k.get_value()
        m = (d + k) / 2
        is_maj = m >= S
        rt = 0.6 if self.frozen else [1.0, 0.6, 0.35][level]

        self.m_tr.set_value(m)
        M = self.make_marker(self.m_tr, "M", COL_M)
        self.play(Transform(self.slab, self.step_label(n)), FadeIn(M, shift=DOWN * 0.3), run_time=rt)

        xd, xm, xk = self.sx(d), self.sx(m), self.sx(k)
        tmp = VGroup()
        if level == 0:
            b1 = BraceBetweenPoints([xd, AY - 0.75, 0], [xm, AY - 0.75, 0], direction=DOWN, color=COL_M)
            b2 = BraceBetweenPoints([xm, AY - 0.75, 0], [xk, AY - 0.75, 0], direction=DOWN, color=COL_M)
            mid = fr("M est le milieu de [D, K]", 26, COL_M).move_to(DOWN * 1.9)
            self.play(GrowFromCenter(b1), GrowFromCenter(b2), FadeIn(mid), run_time=1)
            self.wait(0.6)
            self.play(FadeOut(VGroup(b1, b2, mid)), run_time=0.5)

        # zone balayée : à droite de M
        h = 0.55
        scan = Polygon([xm, AY - h, 0], [X1 + 0.3, AY - h, 0], [X1 + 0.3, AY + h, 0], [xm, AY + h, 0],
                       stroke_width=0, fill_color=COL_M, fill_opacity=0.22)
        if level < 2:
            q = fr("M est-il un majorant de A ?", 32 if level == 0 else 26, COL_M).move_to(DOWN * 1.9)
            tmp.add(q)
            anims = [FadeIn(q)]
            if level == 0:
                q2 = fr("y a-t-il des éléments de A à droite de M ?", 24, GREY_B).next_to(q, DOWN, buff=0.2)
                tmp.add(q2)
                anims.append(FadeIn(q2))
            self.play(GrowFromEdge(scan, LEFT), *anims, run_time=rt * 1.2)
            if level == 0:
                self.wait(0.8)
        else:
            self.play(GrowFromEdge(scan, LEFT), run_time=rt)

        if not is_maj:
            cand = self.A[self.A > m]
            w = cand[np.argmin(np.abs(cand - (m + S) / 2))]
            pw = np.array([self.sx(w), AY, 0.0])
            ring = Circle(radius=0.18, color=COL_NO, stroke_width=4).move_to(pw)
            wdot = Dot(pw, radius=0.09, color=COL_NO)
            tmp.add(ring, wdot)
            if level < 2:
                v = fr("Non : un élément de A est plus grand que M" if level == 0
                       else "✗  M n'est pas un majorant", 30 if level == 0 else 26, COL_NO)
                v.move_to(DOWN * 3.0)
                tmp.add(v)
                self.play(FadeIn(wdot, scale=1.6), Create(ring), FadeIn(v), run_time=rt)
                self.play(Flash(pw, color=COL_NO, line_length=0.25, flash_radius=0.3), run_time=rt * 0.8)
            else:
                v = fr("✗", 30, COL_NO).move_to([self.sx(m), AY + 1.65, 0])
                tmp.add(v)
                self.play(FadeIn(wdot, scale=1.6), Create(ring), FadeIn(v), run_time=rt)
            if level == 0:
                act = fr("donc D prend la place de M", 28, COL_D).move_to(DOWN * 3.0)
                self.play(ReplacementTransform(v, act))
                tmp.remove(v)
                tmp.add(act)
            self.hist_d.append(d)
            self.play(self.d.animate.set_value(m), FadeOut(M), run_time=rt * 1.3)
        else:
            if level < 2:
                v = fr("Oui : aucun élément de A n'est plus grand que M" if level == 0
                       else "✓  M est un majorant", 30 if level == 0 else 26, COL_K)
                v.move_to(DOWN * 3.0)
                tmp.add(v)
                self.play(scan.animate.set_fill(COL_K, 0.3), FadeIn(v), run_time=rt)
            else:
                v = fr("✓", 30, COL_K).move_to([self.sx(m), AY + 1.65, 0])
                tmp.add(v)
                self.play(scan.animate.set_fill(COL_K, 0.3), FadeIn(v), run_time=rt)
            if level == 0:
                act = fr("donc K prend la place de M", 28, COL_K).move_to(DOWN * 3.0)
                self.play(ReplacementTransform(v, act))
                tmp.remove(v)
                tmp.add(act)
            self.hist_k.append(k)
            self.play(self.k.animate.set_value(m), FadeOut(M), run_time=rt * 1.3)

        M.clear_updaters()
        self.remove(M)
        self.D_seq.append(self.d.get_value())
        new_table = self.make_table(n)
        self.play(FadeOut(tmp), FadeOut(scan), Transform(self.table, new_table), run_time=rt)
        if level == 0:
            self.wait(0.5)

    def maybe_zoom(self, level):
        d, k = self.d.get_value(), self.k.get_value()
        lo, hi = self.lo.get_value(), self.hi.get_value()
        if (k - d) < (hi - lo) / 7:
            c, span = (d + k) / 2, 2.6 * (k - d)
            factor = (hi - lo) / span
            badge = fr(f"zoom ×{factor:.0f}", 24, GREY_B).next_to(self.slab, DOWN, aligned_edge=LEFT)
            self.play(FadeIn(badge), run_time=0.3)
            self.zoom_to(c - span / 2, c + span / 2, run_time=[2.0, 1.5, 1.2][level])
            self.play(FadeOut(badge), run_time=0.3)

    # ---------------------------------------------------------- conclusion
    def conclusion(self):
        # 1) Les suites sont adjacentes
        self.play(FadeOut(self.rule), FadeOut(self.table), FadeOut(self.slab))
        adj = VGroup(fr("Donc les suites", 30), MathTex(r"(D_n)", color=COL_D), fr("et", 30),
                     MathTex(r"(K_n)", color=COL_K), fr("sont adjacentes", 30, weight=BOLD)) \
            .arrange(RIGHT, buff=0.2).move_to(UP * 3.2)
        lim = VGroup(fr("elles convergent vers une même limite", 28), MathTex(r"\ell", color=COL_SUP)
                     .scale(1.2)).arrange(RIGHT, buff=0.2).next_to(adj, DOWN, buff=0.3)
        self.play(FadeIn(adj, shift=DOWN * 0.2))
        self.wait(1.5)
        self.play(FadeIn(lim, shift=DOWN * 0.2))

        # 2) Apparition de la limite (pointillés orangés)
        sup_line = always_redraw(lambda: DashedLine(
            [self.sx(S), AY - 0.55, 0], [self.sx(S), AY + 1.2, 0],
            color=COL_SUP, dash_length=0.08, stroke_width=3))
        ell = MathTex(r"\ell", color=COL_SUP).scale(1.0)
        ell.add_updater(lambda mob: mob.move_to([self.sx(S), AY + 1.6, 0]))
        self.play(Create(sup_line), FadeIn(ell))
        self.wait(1.5)

        # 3) Pourquoi cette limite est la borne supérieure
        self.play(FadeOut(self.obs))
        SC = 0.82
        tsz = 26

        def line(*parts, y):
            g = VGroup(*parts).arrange(RIGHT, buff=0.2).scale(SC)
            g.move_to([0, y, 0])
            return g

        def show(*parts, rt=0.7, pause=0.5):
            for part in parts:
                self.play(FadeIn(part, shift=RIGHT * 0.1), run_time=rt)
                self.wait(pause)

        ys = [AY - 0.98 - 0.47 * i for i in range(6)]

        # --- (i) ℓ majore A
        L1 = line(MathTex(r"\forall a\in A,\ \forall n,\ a\le K_n"),
                  MathTex(r"\underset{n\to+\infty}{\Longrightarrow}"),
                  MathTex(r"\forall a\in A,\ a\le\ell"),
                  MathTex(r"\Longrightarrow"),
                  VGroup(MathTex(r"\ell", color=COL_SUP), fr("majore A", tsz, COL_SUP)).arrange(RIGHT, buff=0.15),
                  y=ys[0])
        show(*L1, pause=0.7)
        self.wait(1)

        # --- (ii) ℓ est le plus petit : on prend ℓ − ε un peu plus petit que ℓ
        # rang N (dans la phase sans zoom) où D fait un vrai pas, et ℓ−ε juste avant D_N
        frozen_ns = range(LAST_ZOOM_STEP + 2, len(self.D_seq))
        N = next(n for n in frozen_ns if self.D_seq[n] > self.D_seq[n - 1])
        DN = self.D_seq[N]
        LE = self.D_seq[N - 1] + 0.35 * (DN - self.D_seq[N - 1])      # valeur de ℓ − ε

        L2 = line(fr("Prenons un réel", tsz), MathTex(r"\ell-\varepsilon", color=COL_NO),
                  fr("un peu plus petit que", tsz), MathTex(r"\ell", color=COL_SUP),
                  MathTex(r"\ (\varepsilon>0)"), y=ys[1])
        xe = self.sx(LE)
        e_line = DashedLine([xe, AY - 0.55, 0], [xe, AY + 1.2, 0], color=COL_NO,
                            dash_length=0.08, stroke_width=3)
        e_lab = MathTex(r"\ell-\varepsilon", color=COL_NO).scale(0.8).move_to([xe, AY + 1.6, 0])
        show(L2[0])
        self.play(FadeIn(VGroup(*L2[1:])), Create(e_line), FadeIn(e_lab), run_time=1)
        self.wait(1.2)

        L3 = line(fr("Comme", tsz), MathTex(r"D_n\to\ell", color=COL_D),
                  fr(", à une certaine étape", tsz), MathTex(r"N", color=COL_D),
                  fr(":", tsz), MathTex(rf"D_{{{N}}}>\ell-\varepsilon", color=COL_D), y=ys[2])
        xdn = self.sx(DN)
        dn_mark = VGroup(
            Line([xdn, AY - 0.3, 0], [xdn, AY + 0.3, 0], color=COL_D, stroke_width=6),
            Triangle(fill_color=COL_D, fill_opacity=1, stroke_width=0).scale(0.11).rotate(PI)
            .move_to([xdn, AY + 0.42, 0]),
            MathTex(rf"D_{{{N}}}", color=COL_D).scale(0.75).move_to([xdn, AY + 1.15, 0]))
        span = Arrow([xe, AY + 0.72, 0], [xdn, AY + 0.72, 0], buff=0.05, color=COL_D,
                     stroke_width=3, max_tip_length_to_length_ratio=0.25)
        show(*L3[:3], pause=0.3)
        self.play(FadeIn(L3[3:]), FadeIn(dn_mark, shift=DOWN * 0.2), run_time=0.9)
        self.play(GrowArrow(span), Flash(dn_mark[0].get_top(), color=COL_D, flash_radius=0.3),
                  run_time=0.9)
        self.wait(1.2)

        L4 = line(fr("Or, par construction,", tsz), MathTex(rf"D_{{{N}}}", color=COL_D),
                  fr("n'est pas un majorant de A :", tsz),
                  MathTex(rf"\exists\, a\in A,\ a>D_{{{N}}}", color=COL_NO), y=ys[3])
        cand = self.A[(self.A > DN) & (self.A < S)]
        wa = cand[np.argmin(np.abs(cand - (DN + S) / 2))]
        pa = np.array([self.sx(wa), AY, 0.0])
        w_ring = Circle(radius=0.17, color=COL_NO, stroke_width=4).move_to(pa)
        w_dot = Dot(pa, radius=0.085, color=COL_NO)
        w_lab = MathTex("a", color=COL_NO).scale(0.75).move_to(pa + UP * 0.5)
        show(*L4[:3], pause=0.4)
        self.play(FadeIn(L4[3]), FadeIn(w_dot, scale=1.6), Create(w_ring), FadeIn(w_lab), run_time=1)
        self.wait(1.2)

        L5 = line(fr("donc", tsz), MathTex(r"a>\ell-\varepsilon"), fr(":", tsz),
                  MathTex(r"\ell-\varepsilon", color=COL_NO),
                  fr("n'est pas un majorant de A non plus !", tsz, COL_NO), y=ys[4])
        show(*L5[:2], pause=0.4)
        self.play(FadeIn(L5[2:]), Indicate(e_lab, color=COL_NO, scale_factor=1.3), run_time=1)
        self.wait(1.5)

        L6 = line(MathTex(r"\varepsilon", color=COL_NO), fr("étant quelconque,", tsz),
                  MathTex(r"\ell", color=COL_SUP), fr("est le plus petit des majorants :", tsz, COL_SUP),
                  MathTex(r"\ell=\sup(A)", color=COL_SUP), y=ys[5])
        show(*L6[:2], pause=0.3)
        show(*L6[2:4], pause=0.3)
        self.play(Write(L6[4]), run_time=1.2)
        self.wait(1)
        self.play(FadeOut(VGroup(e_line, e_lab, dn_mark, span, w_ring, w_dot, w_lab)))

        sup_lab = MathTex(r"\sup(A)", color=COL_SUP).scale(0.85)
        sup_lab.add_updater(lambda mob: mob.move_to([self.sx(S), AY + 1.6, 0]))
        self.play(ReplacementTransform(ell, sup_lab))
        ell.clear_updaters()
        self.play(Indicate(sup_lab, color=COL_SUP, scale_factor=1.4))
        self.wait(1)

        # 4) Dézoom : D et K se confondent avec sup(A)
        # (on rend les étiquettes transparentes plutôt que de les retirer de la scène :
        #  un FadeOut casserait le groupe du marqueur et donc sa mise à jour au dézoom)
        self.play(FadeOut(VGroup(adj, lim)), self.D[2].animate.set_opacity(0),
                  self.K[2].animate.set_opacity(0))
        self.zoom_to(*VIEW0, run_time=4.5)
        self.wait(1)

        res = MathTex(r"\lim_{n\to+\infty}D_n=\lim_{n\to+\infty}K_n=\sup(A)", color=COL_SUP).scale(1.05)
        res.move_to(UP * 2.6)
        box = SurroundingRectangle(res, color=COL_SUP, buff=0.22, corner_radius=0.12)
        self.play(Write(res), Create(box), run_time=2)
        self.play(Circumscribe(VGroup(res, box), color=COL_SUP, fade_out=True))
        self.wait(1.5)

        rem = fr("Remarque : ici sup(A) ∉ A, ce n'est pas un maximum.", 22, GREY_B)
        rem.next_to(box, DOWN, buff=0.15)
        self.play(FadeIn(rem))
        self.wait(4)
        self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, VMobject)])
        self.wait(0.5)
