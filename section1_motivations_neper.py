from manim import *
import numpy as np

# Titre de section « 1. Les motivations de Neper » (≈ 5 s)
# Même ambiance que Titre_Histoire_de_logarithmes.mp4 : nuit bleue, étoiles, or.
# Rendu 1080p : manim -qh section1_motivations_neper.py TitreSection1

BG = "#0B1424"
OR = "#F0CF7A"
CREME = "#FFECBE"
POLICE = "DejaVu Serif"


class TitreSection1(Scene):
    def construct(self):
        self.camera.background_color = BG

        # Halo bleu au centre (dégradé radial approximé par des disques)
        halo = VGroup(*[
            Circle(radius=r).set_fill("#1B2E4F", opacity=0.07).set_stroke(width=0)
            for r in np.linspace(1.0, 7.5, 12)
        ])

        # Champ d'étoiles scintillantes
        rng = np.random.default_rng(7)
        etoiles = VGroup()
        for _ in range(160):
            d = Dot(
                point=[rng.uniform(-7.1, 7.1), rng.uniform(-4.0, 4.0), 0],
                radius=rng.uniform(0.006, 0.018),
                color=WHITE,
            )
            d.phase = rng.uniform(0, TAU)
            d.set_opacity(0.6)
            etoiles.add(d)

        temps = ValueTracker(0)

        def scintille(groupe):
            t = temps.get_value()
            for d in groupe:
                d.set_opacity(0.45 + 0.35 * np.sin(d.phase + 3 * t))

        # Titre
        numero = Text("1.", font=POLICE, color=OR, font_size=110)
        titre = Text("Les motivations de Neper", font=POLICE, color=CREME, font_size=84)
        bloc = VGroup(numero, titre).arrange(RIGHT, buff=0.45, aligned_edge=DOWN)
        if bloc.width > 12:
            bloc.scale_to_fit_width(12)
        bloc.move_to(UP * 0.3)

        trait = Line(LEFT, RIGHT, color=OR, stroke_width=3)
        trait.set_width(bloc.width * 0.7).next_to(bloc, DOWN, buff=0.45)

        # Animation
        self.add(halo)
        etoiles.add_updater(scintille)
        self.add(temps)
        self.play(
            FadeIn(etoiles, lag_ratio=0.01),
            FadeIn(halo),
            temps.animate.increment_value(0.8),
            run_time=0.8,
        )
        self.play(
            FadeIn(numero, shift=DOWN * 0.3, scale=1.3),
            temps.animate.increment_value(0.7),
            run_time=0.7,
        )
        self.play(
            Write(titre),
            temps.animate.increment_value(1.6),
            run_time=1.6,
        )
        self.play(
            GrowFromCenter(trait),
            temps.animate.increment_value(0.6),
            run_time=0.6,
        )
        self.play(temps.animate.increment_value(0.8), run_time=0.8)
        self.play(
            FadeOut(VGroup(halo, etoiles, bloc, trait)),
            temps.animate.increment_value(0.5),
            run_time=0.5,
        )
