from manim import *
import numpy as np

# Titre de section « 1. Les motivations de Napier » (≈ 3,7 s)
# Même ambiance que Titre_Histoire_de_logarithmes.mp4 : nuit bleue, étoiles, or.
# Un petit ballon doré roule sous le titre et trace le trait, puis un reflet
# de lumière parcourt les lettres.
# Rendu 1080p à 30 i/s (comme l'autre titre) :
#   manim -qh --fps 30 section1_motivations_neper.py TitreSection1

BG = "#0B1424"
OR = "#F0CF7A"
CREME = "#FFECBE"
POLICE = "DejaVu Serif"


def ballon(c, r, couleurs):
    """Ballon de plage centré en c ; renvoie (ballon, quartiers) : seuls les quartiers tournent."""
    quartiers = VGroup(*[
        AnnularSector(inner_radius=0, outer_radius=r, start_angle=i * PI / 3, angle=PI / 3,
                      fill_color=couleurs[i % 2], fill_opacity=1, stroke_width=0).move_arc_center_to(c)
        for i in range(6)
    ])
    reflet = Circle(radius=r * 0.18).set_fill(WHITE, opacity=0.7).set_stroke(width=0)
    reflet.move_to(c + np.array([-1, 1, 0]) * r * 0.35)
    contour = Circle(radius=r, stroke_color=BLACK, stroke_width=1.5, stroke_opacity=0.6).move_to(c)
    return VGroup(quartiers, reflet, contour), quartiers


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

        horloge = {"t": 0.0}

        def scintille(groupe, dt):
            horloge["t"] += dt
            for d in groupe:
                d.set_opacity(0.45 + 0.35 * np.sin(d.phase + 3 * horloge["t"]))

        # Titre
        numero = Text("1.", font=POLICE, color=OR, font_size=110)
        titre = Text("Les motivations de Napier", font=POLICE, color=CREME, font_size=84)
        bloc = VGroup(numero, titre).arrange(RIGHT, buff=0.45, aligned_edge=DOWN)
        if bloc.width > 12:
            bloc.scale_to_fit_width(12)
        bloc.move_to(UP * 0.3)

        # Le trait doré est tracé par un petit ballon qui roule de gauche à droite
        y_trait = bloc.get_bottom()[1] - 0.45
        x_debut = bloc.get_center()[0] - bloc.width * 0.35
        x_fin = bloc.get_center()[0] + bloc.width * 0.35
        r = 0.16
        progression = ValueTracker(0)

        def x_ballon():
            return x_debut + progression.get_value() * (x_fin - x_debut)

        boule, quartiers = ballon(np.array([x_debut, y_trait + r, 0]), r, (OR, CREME))
        etat = {"x": x_debut}

        def rouler(m):
            x = x_ballon()
            m.shift(RIGHT * (x - etat["x"]))
            quartiers.rotate(-(x - etat["x"]) / r, about_point=quartiers.get_center())
            etat["x"] = x

        boule.add_updater(rouler)
        trait = Line(np.array([x_debut, y_trait, 0]), np.array([x_debut + 0.01, y_trait, 0]),
                     color=OR, stroke_width=3)
        trait.add_updater(lambda m: m.put_start_and_end_on(
            np.array([x_debut, y_trait, 0]), np.array([max(x_ballon(), x_debut + 0.01), y_trait, 0])))

        # Animation (≈ 3,7 s)
        etoiles.add_updater(scintille)
        self.add(halo)
        self.play(
            FadeIn(etoiles, lag_ratio=0.01),
            FadeIn(halo),
            FadeIn(numero, shift=DOWN * 0.4, scale=1.4),
            FadeIn(boule, scale=0.3),
            run_time=0.7,
        )
        self.add(trait)
        self.play(
            LaggedStart(
                Write(titre, run_time=1.2),
                # the ball is not animated itself here, so that it keeps rolling with the line
                progression.animate(run_time=1.3, rate_func=smooth).set_value(1),
                lag_ratio=0.2,
            ),
            run_time=1.6,
        )
        # Reflet de lumière qui parcourt les lettres, étincelle au bout du trait
        self.play(
            LaggedStart(*[lettre.animate(rate_func=there_and_back).set_color(WHITE) for lettre in titre],
                        lag_ratio=0.06),
            Flash(boule.get_center(), color=OR, flash_radius=0.35, line_length=0.18),
            numero.animate(rate_func=there_and_back).set_color(WHITE),
            run_time=0.7,
        )
        self.wait(0.25)
        self.play(FadeOut(VGroup(halo, etoiles, bloc, trait, boule)), run_time=0.4)
