from manim import *


def beach_ball(c, r, colors):
    """Shaded beach ball centred at c. Returns (ball, spin): only `spin` should rotate."""
    # AnnularSector with inner_radius=0 is a pie slice (Sector(radius=...) is ignored in manim 0.18)
    spin = VGroup(*[
        AnnularSector(inner_radius=0, outer_radius=r,
                      start_angle=i * PI / 3, angle=PI / 3,
                      fill_color=colors[i % 2],
                      fill_opacity=1, stroke_width=0).move_arc_center_to(c)
        for i in range(6)
    ])

    # Fixed lighting: light from the upper left
    light_dir = np.array([-1, 1, 0]) / np.sqrt(2)
    shade = VGroup()
    for i in range(8):
        f = i / 8
        layer = Circle(radius=r * (1 - 0.7 * f))
        layer.set_fill(WHITE, opacity=0.07).set_stroke(width=0)
        layer.move_to(c + light_dir * r * 0.45 * f)
        shade.add(layer)
    highlight = Circle(radius=r * 0.12).set_fill(WHITE, opacity=0.6).set_stroke(width=0)
    highlight.move_to(c + light_dir * r * 0.5)
    dark_side = Difference(
        Circle(radius=r).move_to(c),
        Circle(radius=r).move_to(c + light_dir * r * 0.3),
        fill_color=BLACK, fill_opacity=0.3, stroke_width=0,
    )
    outline = Circle(radius=r, stroke_color=BLACK, stroke_width=2.5, stroke_opacity=0.8).move_to(c)

    # Shadow on the axis
    shadow = Ellipse(width=r * 1.8, height=0.1).set_fill(BLACK, opacity=0.5).set_stroke(width=0)
    shadow.move_to(c + DOWN * (r + 0.02))

    ball = VGroup(shadow, spin, VGroup(shade, highlight, dark_side, outline))
    return ball, spin


def colored_tex(*parts, font_size=40):
    """MathTex built from (tex, color) pairs, each part in its own color."""
    tex = MathTex(*[part for part, _ in parts], font_size=font_size)
    for sub, (_, color) in zip(tex, parts):
        sub.set_color(color)
    return tex


def decimal_fr(value):
    """2.5 -> "2{,}50": two decimals with a French decimal comma, for MathTex."""
    return f"{value:.2f}".replace(".", "{,}")


class Multiplications(Scene):
    def construct(self):
        r = 0.4                     # ball radius
        r_small = 0.28              # radius of the second, smaller balls
        delta_t = 0.8               # Δt: time between two stops
        D = np.exp(delta_t)              # where the red ball is after Δt (it starts at 1)
        slow_motion = 2.5           # 1 = normal speed, 2 = twice as slow...
        top_color, bot_color, a_color = BLUE, RED, PURPLE
        W = WHITE
        x0 = -6.5                   # screen position of graduation 0 on both axes
        axis_length = 12            # screen length of the solid part of each axis
        top_y, bot_y = 2.2, -1.75
        top_unit = axis_length / 4  # the top axis runs from 0 to 4 across the same width
        top_arrow_y = top_y + 2 * r + 0.3   # height of the growing double arrows
        bot_arrow_y = bot_y + 2 * r + 0.3
        eq_center = UP * 0.75       # centre of the box between the two axes

        def top_x(v):
            return x0 + v * top_unit

        def bot_x(v):
            return x0 + v

        def label(tex, color, font_size=36):
            return MathTex(tex, color=color, font_size=font_size)

        # Axes: ticks at every graduation, numbers only at the special points
        def make_axis(y, n, unit, numbered):
            line = Line(np.array([x0, y, 0]), np.array([x0 + axis_length, y, 0]),
                        color=GREY_B, stroke_width=2)
            dots = DashedLine(line.get_end(), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            ticks = VGroup(*[Line(np.array([x0 + k * unit, y - 0.1, 0]), np.array([x0 + k * unit, y + 0.1, 0]),
                                  color=GREY_B, stroke_width=2) for k in range(n + 1)])
            numbers = VGroup(*[MathTex(str(k), font_size=26).next_to(np.array([x0 + k * unit, y, 0]), DOWN, buff=0.25)
                               for k in numbered])
            return VGroup(line, dots, ticks, numbers)

        top_axis = make_axis(top_y, 4, top_unit, [0])
        bot_axis = make_axis(bot_y, 12, 1, [0, 1])

        # Point P at graduation 0 of the bottom axis, green stars at the starting positions
        p_dot = Dot(np.array([bot_x(0), bot_y, 0]), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)
        top_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(np.array([top_x(0), top_y, 0]))
        bot_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(np.array([bot_x(1), bot_y, 0]))

        # Top ball: y(t) = t.   Bottom ball: x(t) = e^t (velocity = x), so y = ln(x)
        t = ValueTracker(0)
        top_ball, top_spin = beach_ball(np.array([top_x(0), top_y + r, 0]), r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(np.array([bot_x(1), bot_y + r, 0]), r, (bot_color, WHITE))

        def rolling(spin, radius, get_x):
            # the ball follows get_x() and turns as if rolling without slipping on screen
            state = {"x": get_x()}

            def roll(mob, dt):
                x = get_x()
                dx = x - state["x"]
                state["x"] = x
                mob.shift(RIGHT * dx)
                spin.rotate(-dx / radius, about_point=spin.get_center())
            return roll

        top_ball.set_z_index(1)     # balls stay in front of ticks and arrows
        bot_ball.set_z_index(1)
        top_ball.add_updater(rolling(top_spin, r, lambda: top_x(t.get_value())))
        bot_ball.add_updater(rolling(bot_spin, r, lambda: bot_x(np.exp(t.get_value()))))

        # Double arrow that keeps stretching between two moving points
        def growing_arrow(get_start, get_end, color):
            def build():
                start, end = get_start(), get_end()
                if end[0] - start[0] < 0.02:
                    end = start + RIGHT * 0.02
                return DoubleArrow(start, end, buff=0, color=color, stroke_width=4,
                                   tip_length=0.18, max_tip_length_to_length_ratio=0.5)
            arrow = build()
            arrow.add_updater(lambda m: m.become(build()))
            return arrow

        def top_ball_point(y):
            return lambda: np.array([top_x(t.get_value()), y, 0])

        def bot_ball_point(y):
            return lambda: np.array([bot_x(np.exp(t.get_value())), y, 0])

        def roll_to(t_target, speed=1):
            self.play(t.animate.set_value(t_target),
                      run_time=abs(t_target - t.get_value()) * slow_motion / speed, rate_func=linear)

        self.add(top_axis, bot_axis, p_dot, p_label, top_star, bot_star, top_ball, bot_ball)
        self.wait(1.5)

        # ---- 1) Three steps of Δt: the blue ball adds Δt, the red ball multiplies by D ----
        red_names = ["D", "D^{2}", "D^{3}"]
        coefficients = ["", "2", "3"]
        formulas, box = [], None
        top_arrows, bot_arrows, top_labels, bot_labels, top_ticks, bot_ticks = [], [], [], [], [], []

        for k in range(1, 4):
            t_start = (k - 1) * delta_t
            top_arrow = growing_arrow(lambda ts=t_start: np.array([top_x(ts), top_arrow_y, 0]),
                                      top_ball_point(top_arrow_y), top_color)
            bot_arrow = growing_arrow(lambda: np.array([bot_x(1), bot_arrow_y, 0]),
                                      bot_ball_point(bot_arrow_y), bot_color)
            self.add(top_arrow, bot_arrow)
            roll_to(k * delta_t)
            top_arrow.clear_updaters()
            bot_arrow.clear_updaters()

            top_label = label(r"\Delta t", top_color).next_to(top_arrow, UP, buff=0.15)
            bot_label = label(red_names[k - 1], bot_color).next_to(bot_arrow, UP, buff=0.15)
            self.play(FadeIn(top_label), FadeIn(bot_label))
            self.play(Wiggle(top_label), Wiggle(bot_label))

            # New formula in the box, next to the previous ones
            formula = colored_tex((r"\ln(", W), (red_names[k - 1], bot_color), (")", W), ("=", W),
                                  (coefficients[k - 1] + r"\Delta t", top_color))
            formulas.append(formula)
            target = VGroup(*[f.copy() for f in formulas]).arrange(RIGHT, buff=0.8).move_to(eq_center)
            formula.move_to(target[-1])
            new_box = SurroundingRectangle(target, color=WHITE, buff=0.25, corner_radius=0.1)
            if box is None:
                box = new_box
                self.play(Create(box), Write(formula))
            else:
                self.play(*[f.animate.move_to(tf) for f, tf in zip(formulas[:-1], target[:-1])],
                          Transform(box, new_box), Write(formula))

            # Graduations marking where the balls are now
            top_tick = Line(UP * 0.15, DOWN * 0.15, color=top_color, stroke_width=5).move_to(
                np.array([top_x(k * delta_t), top_y, 0]))
            bot_tick = Line(UP * 0.15, DOWN * 0.15, color=bot_color, stroke_width=5).move_to(
                np.array([bot_x(D ** k), bot_y, 0]))
            self.play(Create(top_tick), Create(bot_tick))

            # The double arrows come down onto the axes (the red ones stack under each other),
            # their values written underneath
            bot_level = bot_y - 0.75 * (k - 1)
            self.play(
                top_arrow.animate.shift(UP * (top_y - top_arrow_y)),
                top_label.animate.move_to(np.array([top_arrow.get_center()[0], top_y - 0.38, 0])),
                bot_arrow.animate.shift(UP * (bot_level - bot_arrow_y)),
                bot_label.animate.move_to(np.array([bot_arrow.get_center()[0], bot_level - 0.38, 0])),
            )
            self.wait(1)

            top_arrows.append(top_arrow)
            bot_arrows.append(bot_arrow)
            top_labels.append(top_label)
            bot_labels.append(bot_label)
            top_ticks.append(top_tick)
            bot_ticks.append(bot_tick)

        self.wait(3)

        # ---- 2) Values move onto the graduations, arrows go, ln(D^n) = n ln(D) = n Δt ----
        top_tick_labels = [label(coefficients[i] + r"\Delta t", top_color).next_to(top_ticks[i], DOWN, buff=0.12)
                           for i in range(3)]
        bot_tick_labels = [label(red_names[i], bot_color).next_to(bot_ticks[i], DOWN, buff=0.12)
                           for i in range(3)]
        self.play(*[ReplacementTransform(a, b) for a, b in zip(top_labels + bot_labels,
                                                              top_tick_labels + bot_tick_labels)],
                  *[FadeOut(a) for a in top_arrows + bot_arrows], run_time=1.5)

        general = colored_tex((r"\ln(", W), ("D^{n}", bot_color), (")", W), ("=", W), (r"n\ln(", W),
                              ("D", bot_color), (")", W), ("=", W), (r"n\,\Delta t", top_color)).move_to(eq_center)
        self.play(ReplacementTransform(VGroup(*formulas), general),
                  Transform(box, SurroundingRectangle(general, color=WHITE, buff=0.25, corner_radius=0.1)),
                  run_time=1.5)
        self.wait(1.5)

        # ---- 3) Back to the start, then half a step: the square root ----
        self.play(t.animate.set_value(0), run_time=2.5, rate_func=smooth)

        top_arrow = growing_arrow(lambda: np.array([top_x(0), top_arrow_y, 0]), top_ball_point(top_arrow_y), top_color)
        bot_arrow = growing_arrow(lambda: np.array([bot_x(1), bot_arrow_y, 0]), bot_ball_point(bot_arrow_y), bot_color)
        self.add(top_arrow, bot_arrow)
        roll_to(delta_t / 2)

        top_label = label(r"\tfrac{1}{2}\,\Delta t", top_color).next_to(top_arrow, UP, buff=0.15)
        bot_label = label(r"\sqrt{D} = D^{1/2}", bot_color).next_to(bot_arrow, UP, buff=0.15)
        self.play(FadeIn(top_label), FadeIn(bot_label))
        self.play(Wiggle(top_label), Wiggle(bot_label))

        def power_formula(c, text=None):
            # ln(D^c) = c Δt, with c written with a decimal comma
            text = text or decimal_fr(c)
            return colored_tex((r"\ln(", W), ("D^{" + text + "}", bot_color), (")", W), ("=", W),
                               (text + r"\,\Delta t", top_color))

        # The box is sized for the widest content it will hold ("3,00")
        layout = VGroup(general.copy(), power_formula(3)).arrange(RIGHT, buff=0.8).move_to(eq_center)
        power = power_formula(0.5, "0{,}5").move_to(layout[1]).align_to(layout[1], LEFT)
        self.play(general.animate.move_to(layout[0]),
                  Transform(box, SurroundingRectangle(layout, color=WHITE, buff=0.25, corner_radius=0.1)),
                  Write(power))
        self.wait(1.5)

        # ---- 4) The balls move on slowly: the exponent follows, it can be any real number ----
        self.play(FadeOut(top_label), FadeOut(bot_label))

        def update_power(m):
            new = power_formula(t.get_value() / delta_t).move_to(layout[1]).align_to(layout[1], LEFT)
            m.become(new)

        power.add_updater(update_power)
        roll_to(3 * delta_t, speed=1 / 1.5)
        power.clear_updaters()
        top_arrow.clear_updaters()
        bot_arrow.clear_updaters()
        self.wait(1)

        alpha = colored_tex((r"\ln(", W), (r"D^{\alpha}", bot_color), (")", W), ("=", W), (r"\alpha\ln(", W),
                            ("D", bot_color), (")", W), ("=", W), (r"\alpha\,\Delta t", top_color)).move_to(general)
        self.play(ReplacementTransform(general, alpha), run_time=1.5)
        self.play(Circumscribe(alpha, color=YELLOW))
        alpha_target = alpha.copy().move_to(eq_center)
        self.play(FadeOut(power), FadeOut(top_arrow), FadeOut(bot_arrow),
                  alpha.animate.move_to(eq_center),
                  Transform(box, SurroundingRectangle(alpha_target, color=WHITE, buff=0.25, corner_radius=0.1)))
        self.wait(1)

        # ---- 5) A moves freely: the red ball follows A, the blue ball follows ln(A) ----
        self.play(t.animate.set_value(0), run_time=2.5, rate_func=smooth)

        A = ValueTracker(1)
        shift_t = ValueTracker(0)   # 0: red ball on A;  Δt: red ball on A × D
        t.add_updater(lambda m: m.set_value(np.log(A.get_value()) + shift_t.get_value()))
        self.add(t)

        def sweep(start=None):
            # A goes (back to `start`, then) from 1 to 5, then back to 2
            if start is not None:
                self.play(A.animate.set_value(start), run_time=1, rate_func=smooth)
            self.play(A.animate.set_value(5), run_time=2.5, rate_func=smooth)
            self.play(A.animate.set_value(2), run_time=1.8, rate_func=smooth)

        def marker(get_value, color, tex):
            tick = Line(DOWN * 0.3, UP * 0.3, color=color, stroke_width=7)
            tick.add_updater(lambda m: m.move_to(np.array([bot_x(get_value()), bot_y, 0])))
            name = MathTex(tex, color=color, font_size=40)
            name.add_updater(lambda m: m.move_to(np.array([bot_x(get_value()), bot_y - 0.85, 0])))
            tick.update()
            name.update()
            return tick, name

        a_tick, a_name = marker(A.get_value, a_color, "A")
        self.play(Create(a_tick), Write(a_name))
        sweep()

        # ---- 6) A × D: the red ball now sits on A × D ----
        ad_tick, ad_name = marker(lambda: A.get_value() * D, PURE_RED, r"A \times D")
        self.play(Create(ad_tick), Write(ad_name))
        self.play(shift_t.animate.set_value(delta_t), run_time=2, rate_func=smooth)
        sweep(start=1)

        # ---- 7) A second, smaller ball on each axis: on A (red) and on ln(A) (blue) ----
        small_top, small_top_spin = beach_ball(np.array([top_x(np.log(A.get_value())), top_y + r_small, 0]),
                                               r_small, (top_color, YELLOW))
        small_bot, small_bot_spin = beach_ball(np.array([bot_x(A.get_value()), bot_y + r_small, 0]),
                                               r_small, (bot_color, WHITE))
        small_top.set_z_index(1)
        small_bot.set_z_index(1)
        small_top.add_updater(rolling(small_top_spin, r_small, lambda: top_x(np.log(A.get_value()))))
        small_bot.add_updater(rolling(small_bot_spin, r_small, lambda: bot_x(A.get_value())))
        self.play(FadeIn(small_top, scale=0.3), FadeIn(small_bot, scale=0.3))
        sweep(start=1)

        # The two blue balls are always Δt apart
        gap = DoubleArrow(np.array([top_x(0), top_arrow_y, 0]), np.array([top_x(delta_t), top_arrow_y, 0]), buff=0,
                          color=top_color, stroke_width=4, tip_length=0.18)
        gap.add_updater(lambda m: m.move_to(np.array([top_x(np.log(A.get_value()) + delta_t / 2), top_arrow_y, 0])))
        gap.update()
        gap_label = label(r"\Delta t", top_color)
        gap_label.add_updater(lambda m: m.next_to(gap, UP, buff=0.15))
        gap_label.update()
        self.play(GrowFromCenter(gap), FadeIn(gap_label))
        self.play(Wiggle(gap_label))
        self.play(A.animate.set_value(5), run_time=2.5, rate_func=smooth)
        self.play(A.animate.set_value(2), run_time=1.8, rate_func=smooth)

        # ---- 8) The highlight: ln(A × D) = ln(A) + ln(D) ----
        prop = colored_tex((r"\ln(", W), ("A", a_color), (r"\times", W), ("D", bot_color), (")", W), ("=", W),
                           (r"\ln(", W), ("A", a_color), (")", W), ("+", W),
                           (r"\ln(", W), ("D", bot_color), (")", W), font_size=52).move_to(eq_center)
        self.play(FadeOut(alpha, shift=UP * 0.3),
                  Transform(box, SurroundingRectangle(prop, color=WHITE, buff=0.3, corner_radius=0.1)))
        self.play(Write(prop), run_time=2.5)
        self.play(Circumscribe(prop, color=YELLOW, fade_out=True), run_time=1.5)
        self.play(Indicate(prop[1], color=a_color), Indicate(prop[3], color=bot_color),
                  Indicate(prop[7], color=a_color), Indicate(prop[11], color=bot_color))
        self.wait(3)
