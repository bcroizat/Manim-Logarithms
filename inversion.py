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


class Inversion(MovingCameraScene):
    def construct(self):
        r = 0.4                     # ball radius
        slow_motion = 3             # seconds of video per unit of t
        graph_speed = 2             # seconds per unit of t while a graph is drawn
        top_color, bot_color = BLUE, RED
        ln_color, exp_color = YELLOW, GREEN     # colours of the two graphs
        top_y, bot_y = 2.2, -1.75
        e = np.exp(1)
        edge = config.frame_x_radius
        t = ValueTracker(0)

        # Top axis from -4 to 8, bottom axis from 0 to 12, same scale (1 graduation = 1 unit)
        def top_x(v):
            return -2.5 + v

        def bot_x(v):
            return -6.5 + v

        def number(value, color=WHITE, font_size=48):
            return DecimalNumber(value, num_decimal_places=2, color=color, font_size=font_size,
                                 group_with_commas=False)

        def dotted(x_start, x_end, y):
            return DashedLine(np.array([x_start, y, 0]), np.array([x_end, y, 0]),
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)

        def make_axis(y, values, to_x, dots_left):
            line = Line(np.array([to_x(values[0]), y, 0]), np.array([to_x(values[-1]), y, 0]),
                        color=GREY_B, stroke_width=2)
            dots = VGroup(dotted(to_x(values[-1]), edge, y))
            if dots_left:
                dots.add(dotted(-edge, to_x(values[0]), y))
            ticks = VGroup(*[Line(np.array([to_x(k), y - 0.1, 0]), np.array([to_x(k), y + 0.1, 0]),
                                  color=GREY_B, stroke_width=2) for k in values])
            numbers = VGroup(*[MathTex(str(k), font_size=26).next_to(np.array([to_x(k), y, 0]), DOWN, buff=0.25)
                               for k in values])
            return VGroup(dots, line, ticks, numbers)

        top_axis = make_axis(top_y, list(range(-4, 9)), top_x, dots_left=True)
        bot_axis = make_axis(bot_y, list(range(0, 13)), bot_x, dots_left=False)

        # The graduation e on the bottom axis, clearly visible
        e_tick = Line(DOWN * 0.18, UP * 0.18, color=bot_color, stroke_width=6).move_to(np.array([bot_x(e), bot_y, 0]))
        e_label = MathTex("e", color=bot_color, font_size=40).next_to(e_tick, DOWN, buff=0.45)

        # Point P, green stars at the starting positions (0 on top, 1 below)
        p_dot = Dot(np.array([bot_x(0), bot_y, 0]), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)
        stars = VGroup(
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(np.array([top_x(0), top_y, 0])),
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(np.array([bot_x(1), bot_y, 0])),
        )

        # Balls: y = t on top, x = e^t below, so that y = ln(x) and x = e^y
        top_ball, top_spin = beach_ball(np.array([top_x(0), top_y + r, 0]), r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(np.array([bot_x(1), bot_y + r, 0]), r, (bot_color, WHITE))

        def rolling(spin, radius, get_pos, direction=RIGHT):
            # the ball follows get_pos() (a number along `direction`) and turns as if rolling
            state = {"pos": get_pos()}

            def roll(mob, dt):
                pos = get_pos()
                mob.shift(direction * (pos - state["pos"]))
                spin.rotate(-(pos - state["pos"]) / radius, about_point=spin.get_center())
                state["pos"] = pos
            return roll

        top_ball.add_updater(rolling(top_spin, r, lambda: top_x(t.get_value())))
        bot_ball.add_updater(rolling(bot_spin, r, lambda: bot_x(np.exp(t.get_value()))))

        # Leaning arrows with the current positions under their tails
        def lean_arrow(get_tip, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            arrow.add_updater(lambda m: m.shift(get_tip() + DOWN * 0.08 - m.get_end()))
            arrow.update()
            return arrow

        top_arrow = lean_arrow(lambda: np.array([top_x(t.get_value()), top_y, 0]), top_color)
        bot_arrow = lean_arrow(lambda: np.array([bot_x(np.exp(t.get_value())), bot_y, 0]), bot_color)

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

        # Time box in the upper left corner (sized for negative times)
        t_display = VGroup(MathTex("t =", font_size=40), number(0, WHITE, 40))
        t_box = SurroundingRectangle(VGroup(MathTex("t =", font_size=40), number(-4, WHITE, 40)).arrange(RIGHT, buff=0.2),
                                     color=WHITE, buff=0.15, corner_radius=0.1).to_corner(UL, buff=0.25)

        def update_time(m):
            m[1].set_value(t.get_value())
            m.arrange(RIGHT, buff=0.2).move_to(t_box)
        t_display.add_updater(update_time)
        t_display.update()

        def roll_to(t_target, speed=1, *animations):
            self.play(t.animate(rate_func=linear).set_value(t_target), *animations,
                      run_time=abs(t_target - t.get_value()) * slow_motion / speed)

        self.add(top_axis, bot_axis, e_tick, e_label, p_dot, p_label, stars, top_ball, bot_ball,
                 top_arrow, bot_arrow, y_read, x_read, t_box, t_display)
        self.wait(1)

        # ---- 1) t > 0, short stop when the red ball is on e ----
        roll_to(1)
        self.play(Flash(e_tick.get_center(), color=YELLOW, flash_radius=0.35),
                  Indicate(e_label, color=YELLOW), Indicate(x_read, color=YELLOW))
        self.wait(0.5)

        # A big arrow goes up from the bottom axis to the top one: x -> y is the logarithm
        big_arrow = Arrow(np.array([6.2, bot_y + 0.35, 0]), np.array([6.2, top_y - 0.35, 0]), buff=0,
                          color=YELLOW, stroke_width=10, max_tip_length_to_length_ratio=0.15)
        arrow_name = MathTex(r"\ln", color=YELLOW, font_size=48).next_to(big_arrow, LEFT, buff=0.2)
        roll_to(2.2, 1, GrowArrow(big_arrow), Write(arrow_name))
        roll_to(1.2, 1, ShowPassingFlash(big_arrow.copy().set_color(WHITE), time_width=0.5),
                Indicate(arrow_name, color=WHITE))

        # The arrow gives way to the central box: ln(x) = y  ->  ln(2.72) = 1.00
        eq_center = UP * 0.2

        def colored_tex(*parts, font_size=44):
            tex = MathTex(*[p for p, _ in parts], font_size=font_size)
            for sub, (_, color) in zip(tex, parts):
                sub.set_color(color)
            return tex

        generic_ln = colored_tex((r"\ln(", WHITE), ("x", bot_color), (")", WHITE), ("=", WHITE), ("y", top_color))
        to_live = MathTex(r"\longrightarrow", font_size=44)

        def ln_live(x_value, y_value):
            return VGroup(MathTex(r"\ln(", font_size=44), number(x_value, bot_color, 44), MathTex(")", font_size=44),
                          MathTex("=", font_size=44), number(y_value, top_color, 44))

        def arrange_ln_live(m):
            m.arrange(RIGHT, buff=0.1)
            m[3].shift(RIGHT * 0.06)
            m[4].shift(RIGHT * 0.12)

        ln_widest = ln_live(12, -4)
        arrange_ln_live(ln_widest)
        ln_layout = VGroup(generic_ln.copy(), to_live.copy(), ln_widest).arrange(RIGHT, buff=0.45).move_to(eq_center)
        generic_ln.move_to(ln_layout[0])
        to_live.move_to(ln_layout[1])
        live_anchor = VectorizedPoint(ln_layout[2].get_center())

        live = ln_live(1, 0)

        def update_ln_live(m):
            s = t.get_value()
            m[1].set_value(np.exp(s))
            m[4].set_value(s)
            arrange_ln_live(m)
            m.move_to(live_anchor.get_center())

        update_ln_live(live)

        def frame_box(content):
            return SurroundingRectangle(content, color=WHITE, buff=0.25, corner_radius=0.1)

        box = frame_box(ln_layout)
        roll_to(0.6, 1, FadeOut(big_arrow, shift=UP * 0.5), FadeOut(arrow_name, shift=UP * 0.5),
                Create(box), Write(generic_ln))
        roll_to(1.6, 1, Write(to_live), FadeIn(live, shift=LEFT * 0.3))
        live.add_updater(update_ln_live)
        self.add(live_anchor)

        # The balls keep moving, now also with t < 0, then back to the start
        roll_to(0)
        roll_to(-3)
        self.wait(0.5)
        roll_to(0)
        self.wait(1)

        # ---- 2) Zoom out: the figure goes left, the graph of ln is drawn on the right ----
        frame = self.camera.frame

        def zoom_out():
            self.play(frame.animate.scale(2).move_to(RIGHT * edge), run_time=2.5, rate_func=smooth)

        def zoom_in(*animations):
            self.play(frame.animate.scale(0.5).move_to(ORIGIN), *animations, run_time=2.5, rate_func=smooth)

        def graph_scene(x_range, y_range, h_name, h_color, v_name, v_color, h_value, v_value,
                        h_ball_colors, v_ball_colors, curve_color):
            """Axes on the right half of the zoomed-out view, with a miniature ball on each axis
            (at h_value(t) and v_value(t)), dashed lines to the point and its traced path."""
            axes = Axes(x_range=x_range, y_range=y_range, x_length=12.5, y_length=13,
                        axis_config={"color": GREY_B, "stroke_width": 4, "include_numbers": True,
                                     "font_size": 40, "tip_width": 0.4, "tip_height": 0.4},
                        ).move_to(np.array([14.6, 0, 0]))
            labels = VGroup(
                MathTex(h_name, color=h_color, font_size=64).next_to(axes.x_axis.get_end(), DOWN, buff=0.35),
                MathTex(v_name, color=v_color, font_size=64).next_to(axes.y_axis.get_end(), RIGHT, buff=0.35),
            )
            rm = 0.4                                 # miniature balls (half size once zoomed out)
            h_ball, h_spin = beach_ball(axes.c2p(h_value(t.get_value()), 0) + UP * rm, rm, h_ball_colors)
            v_ball, v_spin = beach_ball(axes.c2p(0, v_value(t.get_value())) + LEFT * rm, rm, v_ball_colors)
            h_ball.add_updater(rolling(h_spin, rm, lambda: axes.c2p(h_value(t.get_value()), 0)[0]))
            v_ball.add_updater(rolling(v_spin, rm, lambda: axes.c2p(0, v_value(t.get_value()))[1], UP))

            def point():
                s = t.get_value()
                return axes.c2p(h_value(s), v_value(s))

            dot = Dot(point(), color=curve_color, radius=0.13)
            dot.add_updater(lambda m: m.move_to(point()))

            def dashed(start):
                end = point()
                if np.linalg.norm(end - start) < 0.1:
                    end = start + RIGHT * 0.1
                return DashedLine(start, end, dash_length=0.15, dashed_ratio=0.5, color=GREY_A, stroke_width=3)

            h_dash = dashed(axes.c2p(h_value(t.get_value()), 0))
            h_dash.add_updater(lambda m: m.become(dashed(axes.c2p(h_value(t.get_value()), 0))))
            v_dash = dashed(axes.c2p(0, v_value(t.get_value())))
            v_dash.add_updater(lambda m: m.become(dashed(axes.c2p(0, v_value(t.get_value())))))
            trace = TracedPath(dot.get_center, stroke_color=curve_color, stroke_width=7)
            return axes, labels, VGroup(h_ball, v_ball), VGroup(h_dash, v_dash), dot, trace

        def draw_graph(parts):
            axes, labels, balls, dashes, dot, trace = parts
            self.play(Create(axes), Write(labels), run_time=2)
            self.play(FadeIn(balls, scale=0.3))
            self.play(Create(dashes), FadeIn(dot, scale=0.5))
            self.add(trace)
            for target in [np.log(12), -4, 0]:
                self.play(t.animate(rate_func=smooth).set_value(target),
                          run_time=abs(target - t.get_value()) * graph_speed)
            self.wait(4)                             # long pause on the finished graph

        zoom_out()
        ln_graph = graph_scene([0, 12.5, 1], [-4, 3, 1], "x", bot_color, "y", top_color,
                               np.exp, lambda s: s, (bot_color, WHITE), (top_color, YELLOW), ln_color)
        draw_graph(ln_graph)
        zoom_in(*[FadeOut(m) for m in ln_graph])
        self.wait(1)

        # ---- 3) The arrow comes back and turns round: x = e^y ----
        self.play(FadeIn(big_arrow), FadeIn(arrow_name))
        self.play(Rotate(big_arrow, PI), run_time=2.5, rate_func=smooth)
        exp_name = MathTex(r"\exp", color=YELLOW, font_size=48).next_to(big_arrow, LEFT, buff=0.2)
        self.play(ReplacementTransform(arrow_name, exp_name),
                  ShowPassingFlash(big_arrow.copy().set_color(WHITE), time_width=0.5), run_time=1.5)

        # The box turns into x = e^y  ->  2.72 = e^1.00
        generic_exp = colored_tex(("x", bot_color), ("=", WHITE), ("e", WHITE), ("^{y}", top_color))

        def exp_live(x_value, y_value):
            return VGroup(number(x_value, bot_color, 44), MathTex("=", font_size=44), MathTex("e", font_size=44),
                          number(y_value, top_color, 30))

        def arrange_exp_live(m):
            m[1].next_to(m[0], RIGHT, buff=0.2)
            m[2].next_to(m[1], RIGHT, buff=0.2)
            m[3].next_to(m[2], RIGHT, buff=0.04).align_to(m[2], UP).shift(UP * 0.18)

        exp_widest = exp_live(12, -4)
        arrange_exp_live(exp_widest)
        exp_layout = VGroup(generic_exp.copy(), to_live.copy(), exp_widest).arrange(RIGHT, buff=0.45).move_to(eq_center)
        exp_live_mob = exp_live(1, 0)

        def update_exp_live(m):
            s = t.get_value()
            m[0].set_value(np.exp(s))
            m[3].set_value(s)
            arrange_exp_live(m)
            m.move_to(live_anchor.get_center())

        live.clear_updaters()
        self.play(live_anchor.animate.move_to(exp_layout[2]), to_live.animate.move_to(exp_layout[1]),
                  Transform(box, frame_box(exp_layout)), run_time=1)
        generic_exp.move_to(exp_layout[0])
        update_exp_live(exp_live_mob)
        self.play(ReplacementTransform(generic_ln, generic_exp), ReplacementTransform(live, exp_live_mob),
                  run_time=2.5)
        exp_live_mob.add_updater(update_exp_live)
        self.play(Circumscribe(generic_exp, color=YELLOW), FadeOut(big_arrow), FadeOut(exp_name))

        # Same moves: positive y (stop at y = 1), back, negative y, back
        roll_to(1)
        self.play(Indicate(y_read, color=YELLOW), Indicate(exp_live_mob, color=YELLOW),
                  Flash(e_tick.get_center(), color=YELLOW, flash_radius=0.35))
        self.wait(0.5)
        roll_to(2.2)
        roll_to(0)
        roll_to(-3)
        self.wait(0.5)
        roll_to(0)
        self.wait(1)

        # ---- 4) Zoom out again: the graph of the exponential is drawn ----
        zoom_out()
        exp_graph = graph_scene([-4, 2.6, 1], [0, 12.5, 1], "y", top_color, "x", bot_color,
                                lambda s: s, np.exp, (top_color, YELLOW), (bot_color, WHITE), exp_color)
        draw_graph(exp_graph)

        # Back to the layout of the start: the video ends there
        zoom_in(*[FadeOut(m) for m in exp_graph])
        self.wait(2)
