from manim import *


class DecimalComma(DecimalNumber):
    """DecimalNumber written with a decimal comma: 2,72 instead of 2.72."""

    def _get_num_string(self, number):
        return super()._get_num_string(number).replace(".", ",")


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


class BaseE(Scene):
    def construct(self):
        r = 0.4                     # ball radius
        slow_motion = 3             # seconds of video per unit of t
        top_color, bot_color = BLUE, RED
        x0 = -6.5                   # screen position of graduation 0 on both axes
        top_y, bot_y = 2.2, -1.75
        e = np.exp(1)

        def number(value, color=WHITE, font_size=48):
            return DecimalComma(value, num_decimal_places=2, color=color, font_size=font_size,
                                group_with_commas=False)

        # Two graduated axes from 0 to 12 (1 graduation = 1 scene unit), each ending in a dotted line
        def make_axis(y):
            line = Line(np.array([x0, y, 0]), np.array([x0 + 12, y, 0]), color=GREY_B, stroke_width=2)
            dots = DashedLine(line.get_end(), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            ticks = VGroup(*[Line(np.array([x0 + k, y - 0.1, 0]), np.array([x0 + k, y + 0.1, 0]),
                                  color=GREY_B, stroke_width=2) for k in range(13)])
            numbers = VGroup(*[MathTex(str(k), font_size=26).next_to(np.array([x0 + k, y, 0]), DOWN, buff=0.25)
                               for k in range(13)])
            return VGroup(line, dots, ticks, numbers)

        top_axis, bot_axis = make_axis(top_y), make_axis(bot_y)

        def bot_point(x):
            return np.array([x0 + x, bot_y, 0])

        # Point P at graduation 0 of the bottom axis, green stars at the starting positions
        p_dot = Dot(bot_point(0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)
        stars = VGroup(
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(np.array([x0, top_y, 0])),
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(bot_point(1)),
        )

        # Top ball: y(t) = t (velocity 1).   Bottom ball: x(t) = e^t (velocity x), so y = ln(x)
        t = ValueTracker(0)
        top_ball, top_spin = beach_ball(np.array([x0, top_y + r, 0]), r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(bot_point(1) + UP * r, r, (bot_color, WHITE))

        def rolling(spin, get_x):
            # the ball follows get_x() and turns as if rolling without slipping
            state = {"x": get_x()}

            def roll(mob, dt):
                x = get_x()
                mob.shift(RIGHT * (x - state["x"]))
                spin.rotate(-(x - state["x"]) / r, about_point=spin.get_center())
                state["x"] = x
            return roll

        top_ball.add_updater(rolling(top_spin, lambda: x0 + t.get_value()))
        bot_ball.add_updater(rolling(bot_spin, lambda: x0 + np.exp(t.get_value())))

        # Arrow under each ball, leaning right so it doesn't cover the axis number under the ball
        def lean_arrow(get_tip, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            arrow.add_updater(lambda m: m.shift(get_tip() + DOWN * 0.08 - m.get_end()))
            arrow.update()
            return arrow

        top_arrow = lean_arrow(lambda: np.array([x0 + t.get_value(), top_y, 0]), top_color)
        bot_arrow = lean_arrow(lambda: bot_point(np.exp(t.get_value())), bot_color)

        # Current positions written under the arrows' tails
        def readout(name, color, arrow, get_value):
            group = VGroup(MathTex(name + " =", color=color, font_size=34), number(0, color, 34))

            def follow(m):
                m[1].set_value(get_value())
                m.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)
            group.add_updater(follow)
            group.update()
            return group

        y_read = readout("y", top_color, top_arrow, t.get_value)
        x_read = readout("x", bot_color, bot_arrow, lambda: np.exp(t.get_value()))

        # Time box in the upper left corner
        t_display = VGroup(MathTex("t =", font_size=40), number(0, WHITE, 40))
        t_box = SurroundingRectangle(VGroup(MathTex("t =", font_size=40), number(0, WHITE, 40)).arrange(RIGHT, buff=0.2),
                                     color=WHITE, buff=0.15, corner_radius=0.1).to_corner(UL, buff=0.25)

        def update_time(m):
            m[1].set_value(t.get_value())
            m.arrange(RIGHT, buff=0.2).move_to(t_box)
        t_display.add_updater(update_time)
        t_display.update()

        # Central box: ln(x) = y with the current values, x in red and y in blue
        eq_anchor = VectorizedPoint(UP * 0.15)  # where the equation sits (it can be moved)

        def ln_equation(x_value, y_value):
            return VGroup(MathTex(r"\ln("), number(x_value, bot_color), MathTex(")"), MathTex("="),
                          number(y_value, top_color))

        def arrange_equation(m):
            m.arrange(RIGHT, buff=0.12)
            m[3].shift(RIGHT * 0.06)                # a little more room around "="
            m[4].shift(RIGHT * 0.12)

        eq = ln_equation(1, 0)

        def update_eq(m):
            s = t.get_value()
            m[1].set_value(np.exp(s))
            m[4].set_value(s)
            arrange_equation(m)
            m.move_to(eq_anchor.get_center())

        eq.add_updater(update_eq)
        eq.update()
        eq_widest = ln_equation(11.59, 2.45)        # widest equation shown (x up to e^2,45)
        arrange_equation(eq_widest)
        eq_widest.move_to(eq_anchor.get_center())

        def frame_box(content, buff=0.3):
            return SurroundingRectangle(content, color=WHITE, buff=buff, corner_radius=0.1)

        box = frame_box(eq_widest)

        def roll_to(t_target, speed=1):
            self.play(t.animate.set_value(t_target),
                      run_time=abs(t_target - t.get_value()) * slow_motion / speed, rate_func=linear)

        self.add(top_axis, bot_axis, p_dot, p_label, stars, top_ball, bot_ball,
                 top_arrow, bot_arrow, y_read, x_read, t_box, t_display, box, eq, eq_anchor)
        self.wait(1)

        # ---- 1) Reminder: the red ball's velocity is its position x, the blue ball's is 1 ----
        v_red = MathTex("v = x", color=bot_color, font_size=40).next_to(bot_ball, RIGHT, buff=0.3)
        v_blue = MathTex("v = 1", color=top_color, font_size=40).next_to(top_ball, RIGHT, buff=0.3)
        self.play(Write(v_red), Write(v_blue))
        self.play(Indicate(v_red, color=YELLOW), Indicate(v_blue, color=YELLOW))
        self.wait(1)
        self.play(FadeOut(v_red), FadeOut(v_blue))

        # ---- 2) Time flows slowly up to exactly t = 1: then x = e ----
        roll_to(1)
        self.wait(0.5)
        x_bold = MathTex(r"x = \mathbf{2{,}72}", color=bot_color, font_size=40).next_to(
            bot_arrow.get_start(), DOWN, buff=0.1)
        x_read.clear_updaters()     # a value cannot keep updating while it is being transformed
        self.play(ReplacementTransform(x_read, x_bold))
        self.play(Circumscribe(x_bold, color=YELLOW))
        x_full = MathTex(r"x = 2{,}7182818\ldots", color=bot_color, font_size=36).next_to(x_bold, DOWN, buff=0.2)
        self.play(Write(x_full), run_time=2)
        self.wait(0.5)

        # e = 2,7182818... joins the central box, next to ln(x) = y
        e_text = MathTex("e", "=", r"2{,}7182818\ldots")
        e_text[2].set_color(bot_color)
        layout = VGroup(eq_widest.copy(), e_text.copy()).arrange(RIGHT, buff=0.8).move_to(UP * 0.15)
        e_text.move_to(layout[1])
        self.play(eq_anchor.animate.move_to(layout[0]),
                  Transform(box, frame_box(layout)),
                  TransformFromCopy(x_full, e_text), run_time=2)
        self.play(Circumscribe(e_text, color=YELLOW))
        self.play(FadeOut(x_full))
        self.wait(1)

        # ---- 3) New graduations on the bottom axis: powers of e ----
        old_ticks = VGroup(*bot_axis[2][2:])
        old_numbers = VGroup(*bot_axis[3][2:])        # 0 and 1 stay
        self.play(LaggedStart(*[FadeOut(n, shift=DOWN * 0.3) for n in old_numbers], lag_ratio=0.06),
                  FadeOut(old_ticks), run_time=1.5)

        powers = [(0.5, r"e^{0{,}5}"), (1, "e"), (1.5, r"e^{1{,}5}"), (2, "e^{2}"), (2.45, r"e^{2{,}45}")]
        e_ticks, e_labels = VGroup(), VGroup()
        for p, tex in powers:
            point = bot_point(np.exp(p))
            e_ticks.add(Line(point + DOWN * 0.13, point + UP * 0.13, color=bot_color, stroke_width=4))
            e_labels.add(MathTex(tex, color=bot_color, font_size=32).next_to(point, DOWN, buff=0.25))
        self.play(LaggedStart(*[AnimationGroup(GrowFromCenter(tk), FadeIn(lb, shift=UP * 0.4))
                                for tk, lb in zip(e_ticks, e_labels)], lag_ratio=0.35), run_time=3)
        self.play(LaggedStart(*[Flash(tk.get_center(), color=YELLOW, flash_radius=0.25, line_length=0.15)
                                for tk in e_ticks], lag_ratio=0.2), run_time=1.5)

        # The red position is now written as a power of e: x = e^y, y being the blue position
        x_exp = VGroup(MathTex("x = e", color=bot_color, font_size=34), number(0, bot_color, 24))

        def follow_exp(m):
            m[1].set_value(t.get_value())
            m[1].next_to(m[0], RIGHT, buff=0.03).align_to(m[0], UP).shift(UP * 0.12)
            m.next_to(bot_arrow.get_start(), DOWN, buff=0.1)

        follow_exp(x_exp)
        self.play(ReplacementTransform(x_bold, x_exp), run_time=1.5)
        x_exp.add_updater(follow_exp)
        self.play(Indicate(x_exp[1], color=YELLOW), Indicate(y_read[1], color=YELLOW))
        self.wait(1)

        # ---- 4) Forward from e to e^2,45 with stops, then back to the start (stop at e^0,5) ----
        def illustrate(i):
            self.play(Flash(e_ticks[i].get_center(), color=YELLOW, flash_radius=0.3, line_length=0.18),
                      Indicate(e_labels[i], color=YELLOW), Indicate(x_exp, color=YELLOW),
                      Indicate(y_read, color=YELLOW))
            self.wait(1)

        for i, p in [(2, 1.5), (3, 2), (4, 2.45)]:
            roll_to(p)
            illustrate(i)
        roll_to(0.5)
        illustrate(0)
        roll_to(0)
        self.wait(1)

        # ---- 5) The balls go back and forth while ln(e^x) = x appears in the box ----
        # The live equation ln(x) = y becomes ln(e^y) = y (since x = e^y)
        def exp_equation(y_value):
            return VGroup(MathTex(r"\ln(", font_size=42), MathTex("e", color=bot_color, font_size=42),
                          number(y_value, bot_color, 28), MathTex(")", font_size=42), MathTex("=", font_size=42),
                          number(y_value, top_color, 42))

        def arrange_exp_equation(m):
            m[0].next_to(m[1], LEFT, buff=0.06)
            m[2].next_to(m[1], RIGHT, buff=0.03).align_to(m[1], UP).shift(UP * 0.15)
            m[3].next_to(m[2], RIGHT, buff=0.06).align_to(m[0], DOWN)
            m[4].next_to(m[3], RIGHT, buff=0.2)
            m[5].next_to(m[4], RIGHT, buff=0.2)

        general = MathTex(r"\ln", "(", "e", "^{x}", ")", "=", "x", font_size=42)
        live_widest = exp_equation(2.45)
        arrange_exp_equation(live_widest)
        column = VGroup(general.copy(), live_widest).arrange(DOWN, buff=0.2)
        final_layout = VGroup(column, e_text.copy()).arrange(RIGHT, buff=0.8).move_to(DOWN * 0.1)
        general.move_to(column[0])
        live_anchor = column[1].get_center()

        live = exp_equation(0)

        def update_live(m):
            s = t.get_value()
            m[2].set_value(s)
            m[5].set_value(s)
            arrange_exp_equation(m)
            m.move_to(live_anchor)

        update_live(live)

        self.play(t.animate.set_value(1.6), run_time=1.6 * slow_motion, rate_func=smooth)
        eq.clear_updaters()
        update_live(live)
        self.play(Transform(box, frame_box(final_layout, buff=0.2)),
                  e_text.animate.move_to(final_layout[1]), ReplacementTransform(eq, live), run_time=1.5)
        live.add_updater(update_live)
        # The back-and-forth motion and the formula animations play together; each keeps
        # its own rate function (a rate_func given to self.play would apply to all of them)
        def swing(t_target, *animations):
            self.play(t.animate(rate_func=smooth).set_value(t_target), *animations,
                      run_time=abs(t_target - t.get_value()) * slow_motion)

        swing(0.6)
        swing(2.2, Write(general))
        # e^x takes the red of the red ball's position, x the blue of the blue ball's
        swing(1.0, Circumscribe(general, color=YELLOW), general[2:4].animate.set_color(bot_color),
              general[6].animate.set_color(top_color))
        swing(2.0, Indicate(live[2], color=YELLOW), Indicate(live[5], color=YELLOW))
        swing(1.0)
        self.wait(3)
