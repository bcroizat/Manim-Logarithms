"""
Théorème de Bolzano–Weierstrass : extraction d'une sous-suite convergente par dichotomie
Manim Community Edition (syntaxe v0.18 / v0.19)

Rendu :
    manim -pqh bolzano_weierstrass.py BolzanoWeierstrass     # 1080p 60 i/s
    manim -pql bolzano_weierstrass.py BolzanoWeierstrass     # aperçu rapide 480p
"""
from manim import *
import numpy as np

# ----------------------------------------------------------------- couleurs
BG = "#0d1117"
COL_AXIS = "#9aa4b2"
COL_TXT = "#e6edf3"
COL_SEQ = "#4fa3ff"     # termes de la suite
COL_IN = "#7cf0ff"      # termes dans l'intervalle courant
COL_BAND = "#a78bfa"    # intervalle courant I_k
COL_KEEP = "#3ddc97"    # moitié conservée (infinité de termes)
COL_REJ = "#ff5c7a"     # moitié rejetée (nombre fini de termes)
COL_PICK = "#f7c948"    # termes choisis (sous-suite)

# ----------------------------------------------------------------- données
N = 60                   # termes affichés u_0 ... u_N
A0, B0 = -2.5, 2.5       # la suite est bornée : u_n ∈ [A0, B0]
L_ODD, L_EVEN = 0.57, -1.05   # valeurs d'adhérence (termes impairs / pairs)
N_STEPS = 7
VIEW0 = (-2.8, 2.8)
PX0, PX1 = -5.4, 3.0     # zone du graphique à l'écran
PY0, PY1 = -3.0, 2.45
PANEL_X = 5.3


def u_seq():
    n = np.arange(N + 1)
    p = 1.25 * np.sin(2.3 * n + 0.4) * 0.9 ** n
    return np.where(n % 2 == 1, L_ODD, L_EVEN) + p


def plan(u, seed=11):
    """Intervalles emboîtés + indices choisis (un peu au hasard) phi(0) < phi(1) < ..."""
    rng = np.random.default_rng(seed)
    clusters = [L_ODD, L_EVEN]
    a, b = A0, B0
    elig = [n for n in range(len(u)) if a <= u[n] <= b]
    cand0 = elig[:3]
    phi = [int(rng.choice(cand0))]
    steps = []
    for _ in range(N_STEPS):
        m = (a + b) / 2
        top_inf = any(m <= c <= b for c in clusters)
        bot_inf = any(a <= c <= m for c in clusters)
        keep_top = top_inf                      # si les deux conviennent : celle du haut
        na, nb = (m, b) if keep_top else (a, m)
        elig = [n for n in range(phi[-1] + 1, len(u)) if na <= u[n] <= nb]
        cand = elig[:4]
        pick = int(rng.choice(cand))
        steps.append(dict(a=a, b=b, m=m, top_inf=top_inf, bot_inf=bot_inf,
                          keep_top=keep_top, na=na, nb=nb, cand=cand, pick=pick))
        phi.append(pick)
        a, b = na, nb
    return phi, steps, cand0


def nice_step(span, target=6):
    raw = span / target
    mag = 10 ** np.floor(np.log10(raw))
    for m in (1, 2, 5, 10):
        if m * mag >= raw * (1 - 1e-9):
            return m * mag
    return 10 * mag


def fr_num(x, dec):
    return f"{x:.{dec}f}".replace(".", ",").replace("-", "−")


def tex_num(x, dec):
    return f"{x:.{dec}f}".replace(".", "{,}")


def fr(s, size=28, color=COL_TXT, **kw):
    return Text(s, font_size=size, color=color, **kw)


def tx(s, color=COL_TXT, scale=0.75):
    return MathTex(s, color=color).scale(scale)


class BolzanoWeierstrass(Scene):
    # ============================================================ utilitaires
    def X(self, n):
        return PX0 + (PX1 - PX0) * n / N

    def Y(self, v):
        lo, hi = self.ylo.get_value(), self.yhi.get_value()
        return PY0 + (PY1 - PY0) * (v - lo) / (hi - lo)

    @staticmethod
    def clipy(y):
        return min(max(y, PY0 - 0.05), PY1 + 0.05)

    def in_view(self, v):
        lo, hi = self.ylo.get_value(), self.yhi.get_value()
        mg = 0.02 * (hi - lo)
        return lo - mg <= v <= hi + mg

    def P(self, n):
        return np.array([self.X(n), self.Y(self.u[n]), 0.0])

    def zoom_to(self, nlo, nhi, run_time=2.0):
        lo0, hi0 = self.ylo.get_value(), self.yhi.get_value()
        c0, s0 = (lo0 + hi0) / 2, hi0 - lo0
        c1, s1 = (nlo + nhi) / 2, nhi - nlo

        def upd(mob, alpha):
            a = smooth(alpha)
            s = s0 * (s1 / s0) ** a
            if abs(s0 - s1) > 1e-12:
                c = c0 + (c1 - c0) * (s0 - s) / (s0 - s1)
            else:
                c = c0 + (c1 - c0) * a
            self.ylo.set_value(c - s / 2)
            self.yhi.set_value(c + s / 2)

        self.play(UpdateFromAlphaFunc(self.ylo, upd), run_time=run_time, rate_func=linear)

    def say(self, *parts, rt=0.6):
        g = VGroup(*parts).arrange(RIGHT, buff=0.15)
        if g.width > 8.8:
            g.scale_to_fit_width(8.8)
        g.move_to([(PX0 + PX1) / 2 - 0.3, 3.45, 0])
        anims = [FadeIn(g, shift=DOWN * 0.2)]
        if self.caption is not None:
            anims.append(FadeOut(self.caption, shift=UP * 0.2))
        self.play(*anims, run_time=rt)
        self.caption = g

    def unsay(self, rt=0.4):
        if self.caption is not None:
            self.play(FadeOut(self.caption), run_time=rt)
            self.caption = None

    # ------------------------------------------------------------- dessins
    def make_yaxis(self):
        lo, hi = self.ylo.get_value(), self.yhi.get_value()
        g = VGroup(Line([PX0 - 0.25, PY0 - 0.1, 0], [PX0 - 0.25, PY1 + 0.1, 0],
                        color=COL_AXIS, stroke_width=2))
        step = nice_step(hi - lo)
        dec = max(0, int(-np.floor(np.log10(step) + 1e-9)))
        for i in range(int(np.ceil(lo / step)), int(np.floor(hi / step)) + 1):
            v = i * step
            y = self.Y(v)
            if PY0 - 0.02 <= y <= PY1 + 0.02:
                g.add(Line([PX0 - 0.33, y, 0], [PX0 - 0.17, y, 0], color=COL_AXIS, stroke_width=2))
                g.add(Line([PX0 - 0.17, y, 0], [PX1 + 0.1, y, 0], color=COL_AXIS,
                           stroke_width=1, stroke_opacity=0.12))
                g.add(fr(fr_num(v, dec), 16, COL_AXIS).next_to([PX0 - 0.35, y, 0], LEFT, buff=0.08))
        return g

    def make_naxis(self):
        y = PY0 - 0.25
        g = VGroup(Arrow([PX0 - 0.25, y, 0], [PX1 + 0.45, y, 0], buff=0, color=COL_AXIS,
                         stroke_width=2, max_tip_length_to_length_ratio=0.03))
        for n in range(0, N + 1, 10):
            x = self.X(n)
            g.add(Line([x, y - 0.07, 0], [x, y + 0.07, 0], color=COL_AXIS, stroke_width=2))
            g.add(fr(str(n), 16, COL_AXIS).move_to([x, y - 0.25, 0]))
        g.add(tx("n", COL_AXIS, 0.7).move_to([PX1 + 0.6, y - 0.2, 0]))
        return g

    def make_band(self):
        op = self.band_op.get_value()
        ya = self.clipy(self.Y(self.a.get_value()))
        yb = self.clipy(self.Y(self.b.get_value()))
        yb = max(yb, ya + 1e-3)
        return Polygon([PX0 - 0.1, ya, 0], [PX1 + 0.1, ya, 0], [PX1 + 0.1, yb, 0], [PX0 - 0.1, yb, 0],
                       stroke_color=COL_BAND, stroke_width=1.8, stroke_opacity=op,
                       fill_color=COL_BAND, fill_opacity=0.14 * op)

    def make_terms(self):
        a, b = self.a.get_value(), self.b.get_value()
        dim = self.dim.get_value()
        band_on = self.band_op.get_value() > 0.5
        last = self.chosen[-1] if self.chosen else -1
        g = VGroup()
        for n, v in enumerate(self.u):
            if n in self.chosen or not self.in_view(v):
                continue
            inb = band_on and (a - 1e-12 <= v <= b + 1e-12)
            if inb and n > last:
                col, op = COL_IN, 1.0
            elif inb:
                col, op = COL_IN, 0.4
            else:
                col, op = COL_SEQ, 0.5 if band_on else 1.0
            op = op * (1 - dim) + 0.13 * dim
            g.add(Dot([self.X(n), self.Y(v), 0], radius=0.055, color=col,
                      fill_opacity=op, stroke_width=0))
        return g

    def make_chosen(self):
        g = VGroup()
        for n in self.chosen:
            if self.in_view(self.u[n]):
                p = self.P(n)
                g.add(Circle(radius=0.14, color=COL_PICK, stroke_width=2.5).move_to(p))
                g.add(Dot(p, radius=0.08, color=COL_PICK))
        return g

    def step_label(self, k):
        return fr(f"Étape {k}", 30, COL_TXT, weight=BOLD).move_to([PANEL_X, 3.3, 0])

    def interval_info(self, k, a, b):
        g = VGroup(
            tx(rf"I_{{{k}}}=[{tex_num(a, 4)}\,;\,{tex_num(b, 4)}]", COL_BAND, 0.6),
            tx(rf"|I_{{{k}}}|=\frac{{b_0-a_0}}{{2^{{{k}}}}}\approx {tex_num(b - a, 4)}", COL_BAND, 0.6),
        ).arrange(DOWN, buff=0.18)
        return g.move_to([PANEL_X, -2.55, 0])

    def panel_entry(self, k, n):
        e = tx(rf"\varphi({k})={n}\ \to\ u_{{{n}}}\approx {tex_num(self.u[n], 3)}", COL_PICK, 0.55)
        e.move_to([PANEL_X, 1.75 - 0.5 * k, 0])
        return e

    # ============================================================== scène
    def construct(self):
        self.camera.background_color = BG
        self.u = u_seq()
        self.phi, self.steps, self.cand0 = plan(self.u)

        self.ylo = ValueTracker(VIEW0[0])
        self.yhi = ValueTracker(VIEW0[1])
        self.a = ValueTracker(A0)
        self.b = ValueTracker(B0)
        self.band_op = ValueTracker(0)
        self.dim = ValueTracker(0)
        self.chosen = []
        self.caption = None

        self.intro_title()
        self.present_sequence()
        self.first_pick()
        for k in range(1, N_STEPS + 1):
            level = 0 if k <= 2 else (1 if k <= 4 else 2)
            self.do_step(k, self.steps[k - 1], level)
        self.final_subsequence()
        self.funnel_view()
        self.theorem_card()

    # ------------------------------------------------------------- titre
    def intro_title(self):
        t1 = fr("Théorème de", 34, GREY_B)
        t2 = fr("Bolzano – Weierstrass", 56, weight=BOLD)
        t2.set_color_by_gradient(COL_IN, COL_BAND, COL_PICK)
        title = VGroup(t1, t2).arrange(DOWN, buff=0.25)
        sub = fr("extraire une sous-suite convergente par dichotomie", 28, GREY_B)
        sub.next_to(title, DOWN, buff=0.5)
        # petite animation : des points qui convergent vers le centre
        rng = np.random.default_rng(1)
        pts = VGroup(*[Dot(radius=0.05, color=COL_PICK, fill_opacity=0.8).move_to(
            [rng.uniform(-6.5, 6.5), rng.uniform(-3.6, 3.6), 0]) for _ in range(30)])
        self.play(LaggedStart(*[FadeIn(p, scale=0.3) for p in pts], lag_ratio=0.03), run_time=1)
        self.play(Write(t1), Write(t2), *[p.animate.move_to(DOWN * 2.6).set_opacity(0) for p in pts],
                  run_time=2)
        self.play(FadeIn(sub, shift=UP * 0.3))
        self.wait(1.8)
        self.play(FadeOut(VGroup(title, sub), shift=UP * 0.5), FadeOut(pts))

    # ---------------------------------------------------------- la suite
    def present_sequence(self):
        self.naxis = self.make_naxis()
        self.yaxis = always_redraw(self.make_yaxis)
        ulab = tx("u_n", COL_AXIS, 0.8).move_to([PX0 - 0.5, PY1 + 0.4, 0])
        self.play(Create(self.naxis), FadeIn(self.yaxis), FadeIn(ulab), run_time=1.2)
        self.ulab = ulab

        static = VGroup(*[Dot(self.P(n), radius=0.055, color=COL_SEQ) for n in range(N + 1)])
        self.say(fr("Une suite réelle"), tx(r"(u_n)_{n\in\mathbb{N}}"))
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in static], lag_ratio=0.08), run_time=4)
        self.remove(static)
        self.terms = always_redraw(self.make_terms)
        self.chosen_mob = always_redraw(self.make_chosen)
        self.add(self.terms, self.chosen_mob)

        self.band = always_redraw(self.make_band)
        self.add(self.band)
        self.bring_to_back(self.band)
        self.say(fr("bornée :"), tx(r"\forall n,\ u_n\in I_0=[a_0\,;\,b_0]=[-2{,}5\,;\,2{,}5]"))
        self.play(self.band_op.animate.set_value(1), run_time=1.2)
        self.Ilab = tx("I_0", COL_BAND, 0.8)
        self.Ilab.add_updater(lambda m: m.move_to(
            [PX1 + 0.45, (self.clipy(self.Y(self.a.get_value())) + self.clipy(self.Y(self.b.get_value()))) / 2, 0]))
        self.play(FadeIn(self.Ilab))
        self.wait(1.5)

        # deux zones d'accumulation : la suite ne converge pas
        z1 = DashedLine([PX0, self.Y(L_ODD), 0], [PX1, self.Y(L_ODD), 0], color=COL_TXT,
                        stroke_width=1.5, dash_length=0.1, stroke_opacity=0.5)
        z2 = DashedLine([PX0, self.Y(L_EVEN), 0], [PX1, self.Y(L_EVEN), 0], color=COL_TXT,
                        stroke_width=1.5, dash_length=0.1, stroke_opacity=0.5)
        self.say(fr("Elle ne converge pas : ses termes oscillent entre deux zones…"))
        self.play(Create(z1), Create(z2), run_time=1.2)
        self.wait(1.5)
        self.say(fr("…mais on va en extraire une sous-suite convergente !", 28, COL_PICK))
        self.play(FadeOut(z1), FadeOut(z2))
        self.wait(1.2)

        self.slab = self.step_label(0)
        ptitle = fr("Sous-suite extraite", 24, COL_PICK).move_to([PANEL_X, 2.4, 0])
        self.info = self.interval_info(0, A0, B0)
        self.play(FadeIn(self.slab), FadeIn(ptitle), FadeIn(self.info))
        self.ptitle = ptitle
        self.entries = VGroup()

    # ---------------------------------------------------- choix d'un terme
    def roulette(self, cand, pick, fast=False):
        ring = Circle(radius=0.17, color=COL_PICK, stroke_width=3).move_to(self.P(cand[0]))
        self.play(FadeIn(ring, scale=1.5), run_time=0.25 if fast else 0.4)
        seq = list(cand[1:]) + list(cand) if not fast else list(cand[1:])
        for c in seq:
            self.play(ring.animate.move_to(self.P(c)), run_time=0.12 if fast else 0.18,
                      rate_func=linear)
        self.play(ring.animate.move_to(self.P(pick)), run_time=0.3)
        self.chosen.append(pick)
        self.play(Flash(self.P(pick), color=COL_PICK, line_length=0.22, flash_radius=0.25),
                  FadeOut(ring), run_time=0.5 if fast else 0.7)

    def first_pick(self):
        self.say(fr("On choisit un premier terme dans"), tx("I_0", COL_BAND), fr(":"),
                 tx(r"u_{\varphi(0)}", COL_PICK))
        n0 = self.phi[0]
        self.roulette(self.cand0, n0)
        e = self.panel_entry(0, n0)
        lab = tx(r"u_{\varphi(0)}", COL_PICK, 0.6).next_to(self.P(n0), UR, buff=0.08)
        self.play(FadeIn(e, shift=LEFT * 0.3), FadeIn(lab))
        self.entries.add(e)
        self.wait(1)
        self.play(FadeOut(lab))

    # -------------------------------------------------------------- étapes
    def do_step(self, k, st, level):
        rt = [1.0, 0.7, 0.45][level]
        a, b, m = st["a"], st["b"], st["m"]
        self.play(Transform(self.slab, self.step_label(k)), run_time=0.4)

        # 1. on coupe l'intervalle en deux
        if level == 0:
            self.say(fr("On coupe"), tx(rf"I_{{{k-1}}}", COL_BAND), fr("en deux moitiés"))
        elif level == 2 and self.steps[k - 2] is not None and k == 5:
            self.say(fr("On recommence : couper, garder la bonne moitié, choisir un terme…", 26))
        ym, ya, yb = self.Y(m), self.Y(a), self.Y(b)
        midline = DashedLine([PX0 - 0.1, ym, 0], [PX1 + 0.1, ym, 0], color=COL_TXT,
                             stroke_width=2.5, dash_length=0.12)

        def half(y0, y1):
            return Polygon([PX0 - 0.1, y0, 0], [PX1 + 0.1, y0, 0], [PX1 + 0.1, y1, 0], [PX0 - 0.1, y1, 0],
                           stroke_width=0, fill_color=COL_TXT, fill_opacity=0.0)

        top, bot = half(ym, yb), half(ya, ym)
        self.add(top, bot)
        self.bring_to_back(top, bot)
        self.bring_to_back(self.band)
        self.play(Create(midline), run_time=rt)

        # 2. combien de termes dans chaque moitié ?
        def verdict(inf):
            if level == 0:
                return fr("une infinité de termes" if inf else "un nombre fini de termes",
                          20, COL_KEEP if inf else COL_REJ)
            return fr("∞" if inf else "fini", 26 if inf else 20, COL_KEEP if inf else COL_REJ)

        vt, vb = verdict(st["top_inf"]), verdict(st["bot_inf"])
        xr = PX1 - 0.15
        vt.move_to([xr - vt.width / 2, (ym + yb) / 2, 0])
        vb.move_to([xr - vb.width / 2, (ya + ym) / 2, 0])
        for v in (vt, vb):
            bg = BackgroundRectangle(v, color=BG, fill_opacity=0.75, buff=0.06)
            v.add_to_back(bg)
        if level == 0:
            self.say(fr("Dans quelle moitié y a-t-il une infinité de termes ?"))
        self.play(
            top.animate.set_fill(COL_KEEP if st["top_inf"] else COL_REJ, 0.16),
            bot.animate.set_fill(COL_KEEP if st["bot_inf"] else COL_REJ, 0.16),
            FadeIn(vt), FadeIn(vb), run_time=rt)
        if level == 0:
            self.wait(1)

        keep, rej = (top, bot) if st["keep_top"] else (bot, top)
        if st["top_inf"] and st["bot_inf"]:
            self.say(fr("Les deux conviennent : on en choisit une, par exemple celle du haut.", 26))
            self.wait(1.5)
        elif level <= 1:
            self.say(fr("On garde la moitié qui contient une infinité de termes", 26, COL_KEEP))
            if level == 0:
                self.wait(0.8)

        # 3. on garde la bonne moitié
        self.play(rej.animate.set_fill(COL_REJ, 0.32), run_time=rt * 0.5)
        self.play(FadeOut(rej), FadeOut(vt), FadeOut(vb), FadeOut(midline),
                  self.a.animate.set_value(st["na"]), self.b.animate.set_value(st["nb"]),
                  run_time=rt * 1.2)
        self.play(FadeOut(keep), run_time=0.3)
        new_I = tx(rf"I_{{{k}}}", COL_BAND, 0.8)
        new_I.move_to(self.Ilab.get_center())
        self.Ilab.become(new_I)
        self.play(Transform(self.info, self.interval_info(k, st["na"], st["nb"])), run_time=0.5)

        # 4. on choisit un terme d'indice plus grand que le précédent
        prev = self.chosen[-1]
        xp = self.X(prev) + 0.5 * (PX1 - PX0) / N
        shade = Polygon([PX0 - 0.1, PY0, 0], [xp, PY0, 0], [xp, PY1, 0], [PX0 - 0.1, PY1, 0],
                        stroke_width=0, fill_color=GREY_D, fill_opacity=0.35)
        vline = DashedLine([xp, PY0, 0], [xp, PY1, 0], color=GREY_B, stroke_width=2, dash_length=0.1)
        if level == 0:
            self.say(fr("On choisit un terme de"), tx(rf"I_{{{k}}}", COL_BAND),
                     fr("d'indice"), tx(rf">\varphi({k-1})={prev}", COL_PICK))
        elif level == 1:
            self.say(tx(rf"u_{{\varphi({k})}}\in I_{{{k}}}\ \text{{et}}\ \varphi({k})>\varphi({k-1})", COL_TXT))
        self.play(FadeIn(shade), Create(vline), run_time=rt * 0.8)
        self.roulette(st["cand"], st["pick"], fast=(level == 2))
        e = self.panel_entry(k, st["pick"])
        self.play(FadeIn(e, shift=LEFT * 0.3), FadeOut(shade), FadeOut(vline), run_time=rt)
        self.entries.add(e)

        # 5. zoom si l'intervalle devient petit
        lo, hi = self.ylo.get_value(), self.yhi.get_value()
        na, nb = st["na"], st["nb"]
        if (nb - na) < (hi - lo) / 4 and k < N_STEPS:
            c, span = (na + nb) / 2, 2.6 * (nb - na)
            factor = (hi - lo) / span
            badge = fr(f"zoom ×{factor:.1f}".replace(".", ","), 22, GREY_B).move_to([PANEL_X, 2.85, 0])
            self.play(FadeIn(badge), run_time=0.3)
            self.zoom_to(c - span / 2, c + span / 2, run_time=[2.0, 1.6, 1.3][level])
            self.play(FadeOut(badge), run_time=0.3)
        if level == 0:
            self.wait(0.5)

    # ---------------------------------------------- visualisation finale
    def final_subsequence(self):
        self.say(fr("Les termes choisis forment la sous-suite"), tx(r"\big(u_{\varphi(k)}\big)_k", COL_PICK))
        self.play(FadeOut(self.Ilab), self.band_op.animate.set_value(0), run_time=0.8)
        self.Ilab.clear_updaters()
        self.zoom_to(*VIEW0, run_time=2.5)
        self.play(self.dim.animate.set_value(1), run_time=1.2)

        pts = [self.P(n) for n in self.chosen]
        path = VMobject(color=COL_PICK, stroke_width=3).set_points_as_corners(pts)
        self.play(Create(path), run_time=3, rate_func=linear)
        labs = VGroup(*[tx(rf"\varphi({k})", COL_PICK, 0.45).next_to(p, UP if k % 2 == 0 else DOWN, buff=0.18)
                        for k, p in enumerate(pts)])
        self.play(LaggedStart(*[FadeIn(l) for l in labs], lag_ratio=0.15), run_time=1.5)
        self.wait(1)
        self.say(fr("avec des indices strictement croissants :"),
                 tx(r"\varphi(0)<\varphi(1)<\varphi(2)<\cdots", COL_PICK))
        self.play(Indicate(self.entries, color=COL_PICK, scale_factor=1.08), run_time=1.5)
        self.wait(1.5)
        self.path, self.labs = path, labs

    def funnel_view(self):
        # on ré-indexe : la k-ième valeur choisie est placée en abscisse k
        self.say(fr("Plaçons-les côte à côte, en fonction de k :"))
        fx = [PX0 + 0.6 + k * (PX1 - PX0 - 1.2) / N_STEPS for k in range(N_STEPS + 1)]
        self.fx = fx
        movers = VGroup(*[Dot(self.P(n), radius=0.09, color=COL_PICK) for n in self.chosen])
        self.add(movers)
        self.remove(self.chosen_mob)
        self.play(FadeOut(self.terms), FadeOut(self.path), FadeOut(self.labs), FadeOut(self.naxis),
                  run_time=1)
        self.remove(self.terms)

        kax_y = PY0 - 0.25
        kaxis = VGroup(Arrow([PX0 - 0.25, kax_y, 0], [PX1 + 0.45, kax_y, 0], buff=0, color=COL_AXIS,
                             stroke_width=2, max_tip_length_to_length_ratio=0.03))
        for k in range(N_STEPS + 1):
            kaxis.add(Line([fx[k], kax_y - 0.07, 0], [fx[k], kax_y + 0.07, 0], color=COL_AXIS, stroke_width=2))
            kaxis.add(fr(str(k), 16, COL_AXIS).move_to([fx[k], kax_y - 0.25, 0]))
        kaxis.add(tx("k", COL_AXIS, 0.7).move_to([PX1 + 0.6, kax_y - 0.2, 0]))
        new_ulab = tx(r"u_{\varphi(k)}", COL_PICK, 0.8).move_to(self.ulab.get_center())
        self.play(Create(kaxis), Transform(self.ulab, new_ulab),
                  *[d.animate.move_to([fx[k], self.Y(self.u[n]), 0])
                    for k, (d, n) in enumerate(zip(movers, self.chosen))], run_time=2)

        # intervalles emboîtés I_0 ⊃ I_1 ⊃ ...
        self.intervals = [(A0, B0)] + [(s["na"], s["nb"]) for s in self.steps]
        funnel = always_redraw(self.make_funnel)
        self.say(fr("Chaque terme appartient à l'intervalle de son étape :"),
                 tx(r"u_{\varphi(k)}\in I_k", COL_BAND))
        self.play(FadeIn(funnel), run_time=1.5)
        self.bring_to_back(funnel)
        self.remove(movers)
        fdots = always_redraw(self.make_fdots)
        self.add(fdots)

        ell_line = always_redraw(lambda: DashedLine(
            [PX0 - 0.15, self.Y(L_ODD), 0], [PX1 + 0.15, self.Y(L_ODD), 0],
            color=COL_KEEP, stroke_width=2.5, dash_length=0.1))
        ell_lab = tx(r"\ell", COL_KEEP, 0.9)
        ell_lab.add_updater(lambda m: m.move_to([PX1 + 0.45, self.Y(L_ODD), 0]))
        self.say(fr("Les intervalles se resserrent sur un unique réel"), tx(r"\ell", COL_KEEP))
        self.play(Create(ell_line), FadeIn(ell_lab), run_time=1.5)
        self.wait(1)

        self.say(fr("Zoom autour de"), tx(r"\ell", COL_KEEP), fr(": la sous-suite converge !", 28, COL_PICK))
        self.zoom_to(L_ODD - 0.07, L_ODD + 0.07, run_time=4)
        self.wait(2)
        self.zoom_to(*VIEW0, run_time=2.5)
        self.say(tx(r"u_{\varphi(k)}\xrightarrow[k\to+\infty]{}\ell", COL_PICK, 1.0))
        self.wait(2)

    def make_funnel(self):
        g = VGroup()
        for k, (a, b) in enumerate(self.intervals):
            ya, yb = self.Y(a), self.Y(b)
            if yb < PY0 - 0.05 or ya > PY1 + 0.05:
                continue
            ya, yb = self.clipy(ya), self.clipy(yb)
            x = self.fx[k]
            g.add(Line([x, ya, 0], [x, max(yb, ya + 0.02), 0], color=COL_BAND,
                       stroke_width=8, stroke_opacity=0.55))
            for yy, yraw in ((ya, a), (yb, b)):
                if self.in_view(yraw):
                    g.add(Line([x - 0.12, yy, 0], [x + 0.12, yy, 0], color=COL_BAND, stroke_width=3))
        return g

    def make_fdots(self):
        g = VGroup()
        pts = []
        for k, n in enumerate(self.chosen):
            v = self.u[n]
            if self.in_view(v):
                p = np.array([self.fx[k], self.Y(v), 0.0])
                pts.append((k, p))
                g.add(Dot(p, radius=0.09, color=COL_PICK))
        for (k1, p1), (k2, p2) in zip(pts, pts[1:]):
            if k2 == k1 + 1:
                g.add(Line(p1, p2, color=COL_PICK, stroke_width=2.5, stroke_opacity=0.8))
        return g

    # ----------------------------------------------------------- théorème
    def theorem_card(self):
        self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, VMobject)], run_time=1.2)
        self.caption = None
        head = fr("Théorème de Bolzano – Weierstrass", 40, weight=BOLD)
        head.set_color_by_gradient(COL_IN, COL_BAND, COL_PICK)
        stmt = fr("Toute suite réelle bornée admet une sous-suite convergente.", 30)
        box = SurroundingRectangle(VGroup(head, stmt).arrange(DOWN, buff=0.3), color=COL_PICK,
                                   buff=0.35, corner_radius=0.15)
        card = VGroup(box, head, stmt).move_to(UP * 2.2)
        self.play(Write(head), run_time=1.5)
        self.play(FadeIn(stmt, shift=UP * 0.2), Create(box))
        self.wait(1)

        l1 = tx(r"I_0\supset I_1\supset I_2\supset\cdots,\qquad |I_k|=\frac{b_0-a_0}{2^k}"
                r"\xrightarrow[k\to+\infty]{}0", COL_BAND, 0.8)
        l2 = tx(r"\varphi(0)<\varphi(1)<\varphi(2)<\cdots\quad\text{et}\quad u_{\varphi(k)}\in I_k",
                COL_PICK, 0.8)
        l3 = tx(r"\Longrightarrow\quad u_{\varphi(k)}\xrightarrow[k\to+\infty]{}\ell", COL_KEEP, 0.9)
        rec = VGroup(l1, l2, l3).arrange(DOWN, buff=0.35).next_to(card, DOWN, buff=0.6)
        for l in rec:
            self.play(FadeIn(l, shift=UP * 0.2), run_time=0.9)
            self.wait(0.7)
        rem = VGroup(fr("Remarque : la suite", 22, GREY_B), tx("(u_n)", GREY_B, 0.7),
                     fr("elle-même ne converge pas !", 22, GREY_B)).arrange(RIGHT, buff=0.12)
        rem.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(rem))
        self.play(Circumscribe(card, color=COL_PICK, fade_out=True), run_time=1.5)
        self.wait(4)
        self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, VMobject)])
        self.wait(0.5)
