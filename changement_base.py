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


class ChangementBase(Scene):
    def construct(self):
        r = 0.4                     # ball radius
        slow_motion = 3             # seconds of video per unit of t
        top_color, bot_color = BLUE, RED
        x0 = -6.5                   # screen position of graduation 0 on both axes
        axis_length = 12            # screen length of the solid part of each axis
        top_y, bot_y = 2.2, -1.75
        edge = config.frame_x_radius
        e = np.exp(1)

        t = ValueTracker(0)         # time; the blue ball is at y = t
        k = ValueTracker(1)         # red ball velocity v = k x, so x = e^(k t) and y = ln(x) / k

        def red_x():
            return np.exp(k.get_value() * t.get_value())

        def number(value, color=WHITE, font_size=48, decimals=2):
            return DecimalNumber(value, num_decimal_places=decimals, color=color, font_size=font_size,
                                 group_with_commas=False)

        def set_x_value(m, value):
            # values below 1 get a third decimal so that 0.001 stays readable
            m.num_decimal_places = 3 if abs(value) < 1 else 2
            m.set_value(value)

        def dotted(x_start, x_end, y):
            x_start = min(max(x_start, -edge), edge - 0.05)
            x_end = max(min(x_end, edge), x_start + 0.05)
            return DashedLine(np.array([x_start, y, 0]), np.array([x_end, y, 0]),
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)

        # ---------------- Top axis: 0..12, later turned into -7..4 (as in BaseE) ----------------
        morph = ValueTracker(0)
        top_k = range(-7, 13)
        new_unit = axis_length / 11         # -7..4 across the same width
        new_zero = x0 + 7 * new_unit

        def top_unit():
            m = morph.get_value()
            return (1 - m) + m * new_unit

        def top_screen(v):
            m = morph.get_value()
            return (1 - m) * (x0 + v) + m * (new_zero + v * new_unit)

        def solid():
            return Line(LEFT, RIGHT, color=GREY_B, stroke_width=2)

        def top_point(x):
            return np.array([x, top_y, 0])

        # pieces: 0..4, -7..0 (fades in), 4..12 (fades out); dotted beyond 12, 4 and -7
        top_main, top_negative, top_beyond = solid(), solid(), solid()
        top_dots_old, top_dots_right, top_dots_left = dotted(x0 + 12, edge, top_y), dotted(x0 + 4, edge, top_y), \
            dotted(-edge, x0 - 7, top_y)
        top_ticks = VGroup(*[Line(DOWN * 0.1, UP * 0.1, color=GREY_B, stroke_width=2) for _ in top_k])
        top_numbers = VGroup(*[MathTex(str(v), font_size=26) for v in top_k])

        def draw_top_axis(group):
            m = morph.get_value()
            top_main.put_start_and_end_on(top_point(top_screen(0)), top_point(top_screen(4)))
            top_negative.put_start_and_end_on(top_point(top_screen(-7)), top_point(top_screen(0)))
            top_negative.set_stroke(opacity=m)
            top_beyond.put_start_and_end_on(top_point(top_screen(4)), top_point(top_screen(12)))
            top_beyond.set_stroke(opacity=1 - m)
            top_dots_old.become(dotted(top_screen(12), edge, top_y)).set_stroke(opacity=1 - m)
            top_dots_right.become(dotted(top_screen(4), edge, top_y)).set_stroke(opacity=m)
            top_dots_left.become(dotted(-edge, top_screen(-7), top_y)).set_stroke(opacity=m)
            for v, tick, num in zip(top_k, top_ticks, top_numbers):
                opacity = m if v < 0 else (1 - m if v > 4 else 1)
                point = top_point(top_screen(v))
                tick.move_to(point).set_stroke(opacity=opacity)
                num.next_to(point, DOWN, buff=0.25).set_opacity(opacity)

        top_axis = VGroup(top_dots_old, top_dots_right, top_dots_left, top_main, top_negative, top_beyond,
                          top_ticks, top_numbers)
        draw_top_axis(top_axis)
        top_axis.add_updater(draw_top_axis)

        # ---------------- Bottom axis: 0..12, zooms in below 1 and out above x_zoom ----------------
        x_zoom = 11.5

        def bot_unit():
            # screen units per graduation: the red ball stays on the screen position of 1 while
            # x < 1 (zoom in), and on the one of x_zoom while x > x_zoom (zoom out)
            x = red_x()
            if x < 1:
                return 1 / x
            return x_zoom / x if x > x_zoom else 1

        def bot_screen(v):
            return x0 + v * bot_unit()

        steps = [m * 10.0 ** p for p in range(-4, 4) for m in (1, 2, 5)]
        min_gap = 0.75                      # minimum screen distance between two numbers
        bot_line = Line(np.array([x0, bot_y, 0]), np.array([x0 + axis_length, bot_y, 0]),
                        color=GREY_B, stroke_width=2)
        bot_dots = dotted(x0 + axis_length, edge, bot_y)
        bot_ticks = VGroup(*[Line(DOWN * 0.1, UP * 0.1, color=GREY_B, stroke_width=2)
                             for _ in range(int(axis_length / (min_gap / 5)) + 3)])
        bot_numbers = VGroup(*[number(0, WHITE, 26, 0) for _ in range(int(axis_length / min_gap) + 2)])
        shown = [None] * len(bot_numbers)

        def draw_bot_axis(group):
            u = bot_unit()
            step = next(s for s in steps if s * u >= min_gap - 1e-9)
            lead = round(step / 10 ** np.floor(np.log10(step) + 1e-9))
            ratio = 2 if lead == 2 else 5
            zoomed = abs(u - 1) > 1e-9
            minor = step / ratio if zoomed else step      # small ticks only while zoomed
            n_ticks = int(axis_length / u / minor + 1e-9) + 1
            decimals = max(0, -int(np.floor(np.log10(step) + 1e-9)))
            for i, tick in enumerate(bot_ticks):
                if i < n_ticks:
                    p = np.array([x0 + i * minor * u, bot_y, 0])
                    major = not zoomed or i % ratio == 0
                    h = 0.1 if major else 0.05
                    tick.put_start_and_end_on(p + DOWN * h, p + UP * h).set_stroke(opacity=1)
                else:
                    tick.set_stroke(opacity=0)
            n_numbers = int(axis_length / u / step + 1e-9) + 1
            for i, num in enumerate(bot_numbers):
                if i < n_numbers:
                    value = round(i * step, 6)
                    if shown[i] != (value, decimals):
                        num.num_decimal_places = decimals
                        num.set_value(value)
                        shown[i] = (value, decimals)
                    num.next_to(np.array([x0 + value * u, bot_y, 0]), DOWN, buff=0.25).set_opacity(1)
                else:
                    num.set_opacity(0)

        bot_graduations = VGroup(bot_ticks, bot_numbers)
        draw_bot_axis(bot_graduations)
        bot_graduations.add_updater(draw_bot_axis)
        bot_axis = VGroup(bot_dots, bot_line, bot_graduations)

        def on_bot_axis(v):
            return 0 <= bot_screen(v) - x0 <= axis_length

        # The graduation e (bright red), the point P and the green stars follow the axes
        e_tick = Line(DOWN * 0.18, UP * 0.18, color=bot_color, stroke_width=6)
        e_label = MathTex("e", color=bot_color, font_size=40)

        def place_e(m):
            e_tick.move_to(np.array([bot_screen(e), bot_y, 0])).set_stroke(opacity=1 if on_bot_axis(e) else 0)
            e_label.next_to(e_tick, DOWN, buff=0.45).set_opacity(1 if on_bot_axis(e) else 0)

        e_mark = VGroup(e_tick, e_label)
        place_e(e_mark)
        e_mark.add_updater(place_e)

        p_dot = Dot(np.array([x0, bot_y, 0]), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)
        top_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1)
        top_star.add_updater(lambda m: m.move_to(top_point(top_screen(0))))
        bot_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1)
        bot_star.add_updater(lambda m: m.move_to(np.array([bot_screen(1), bot_y, 0])).set_opacity(
            1 if on_bot_axis(1) else 0))
        top_star.update()
        bot_star.update()

        # ---------------- Balls ----------------
        top_ball, top_spin = beach_ball(top_point(top_screen(0)) + UP * r, r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(np.array([bot_screen(1), bot_y + r, 0]), r, (bot_color, WHITE))

        def rolling(spin, get_screen_x, get_value, get_unit):
            # the ball follows its screen position and turns by the distance rolled along
            # its axis at the current scale (a change of scale alone does not turn it)
            state = {"x": get_screen_x(), "value": get_value()}

            def roll(mob, dt):
                x, value = get_screen_x(), get_value()
                mob.shift(RIGHT * (x - state["x"]))
                spin.rotate(-(value - state["value"]) * get_unit() / r, about_point=spin.get_center())
                state["x"], state["value"] = x, value
            return roll

        top_ball.add_updater(rolling(top_spin, lambda: top_screen(t.get_value()), t.get_value, top_unit))
        bot_ball.add_updater(rolling(bot_spin, lambda: bot_screen(red_x()), red_x, bot_unit))

        # Leaning arrows; position and velocity written under their tails
        def lean_arrow(get_tip, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            arrow.add_updater(lambda m: m.shift(get_tip() + DOWN * 0.08 - m.get_end()))
            arrow.update()
            return arrow

        top_arrow = lean_arrow(lambda: top_point(top_screen(t.get_value())), top_color)
        bot_arrow = lean_arrow(lambda: np.array([bot_screen(red_x()), bot_y, 0]), bot_color)

        def readouts(name, color, arrow, get_pos, get_vel, adaptive):
            pos = VGroup(MathTex(name + " =", color=color, font_size=34), number(0, color, 34))
            vel = VGroup(MathTex("v =", color=color, font_size=34), number(0, color, 34))

            def follow(m):
                if adaptive:
                    set_x_value(pos[1], get_pos())
                    set_x_value(vel[1], get_vel())
                else:
                    pos[1].set_value(get_pos())
                    vel[1].set_value(get_vel())
                pos.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)
                vel.arrange(RIGHT, buff=0.15).next_to(pos, DOWN, buff=0.15)
                # keep them inside the frame near the right edge
                overflow = VGroup(pos, vel).get_right()[0] - (edge - 0.15)
                if overflow > 0:
                    pos.shift(LEFT * overflow)
                    vel.shift(LEFT * overflow)

            group = VGroup(pos, vel)
            group.add_updater(follow)
            group.update()
            return pos, vel, group

        y_read, top_v_read, top_readouts = readouts("y", top_color, top_arrow, t.get_value, lambda: 1, False)
        x_read, bot_v_read, bot_readouts = readouts("x", bot_color, bot_arrow, red_x,
                                                    lambda: k.get_value() * red_x(), True)

        # Time box in the upper left corner (sized for negative times)
        t_display = VGroup(MathTex("t =", font_size=40), number(0, WHITE, 40))
        t_box = SurroundingRectangle(VGroup(MathTex("t =", font_size=40), number(-3, WHITE, 40)).arrange(RIGHT, buff=0.2),
                                     color=WHITE, buff=0.15, corner_radius=0.1).to_corner(UL, buff=0.25)

        def update_time(m):
            m[1].set_value(t.get_value())
            m.arrange(RIGHT, buff=0.2).move_to(t_box)
        t_display.add_updater(update_time)
        t_display.update()

        def roll_to(t_target, speed=1):
            self.play(t.animate.set_value(t_target),
                      run_time=abs(t_target - t.get_value()) * slow_motion / speed, rate_func=linear)

        def wiggle_values(*mobs):
            self.play(*[Wiggle(m) for m in mobs])

        self.add(top_axis, bot_axis, e_mark, p_dot, p_label, top_star, bot_star, top_ball, bot_ball,
                 top_arrow, bot_arrow, top_readouts, bot_readouts, t_box, t_display)
        self.wait(1)

        # ---- 1) A short trip with v = x (natural base): stop on x = e ----
        roll_to(1)
        self.play(Flash(e_tick.get_center(), color=YELLOW, flash_radius=0.35),
                  Indicate(e_label, color=YELLOW), Indicate(x_read, color=YELLOW))
        self.wait(0.5)
        roll_to(2.4)
        roll_to(0)
        self.wait(0.5)

        # ---- 2) The red velocity box: v = x, then v = k x with k varying ----
        vel_center = np.array([-5.15, 0.05, 0])
        vel_plain = MathTex("v = x", color=bot_color, font_size=44).move_to(vel_center)
        vel_live = VGroup(MathTex("v =", color=bot_color, font_size=44), number(1, bot_color, 44),
                          MathTex("x", color=bot_color, font_size=44))

        def update_vel_live(m):
            m[1].set_value(k.get_value())
            m.arrange(RIGHT, buff=0.15).move_to(vel_center)

        update_vel_live(vel_live)
        vel_box = SurroundingRectangle(vel_live, color=bot_color, buff=0.25, corner_radius=0.1)
        self.play(Create(vel_box), Write(vel_plain))
        self.wait(1)
        self.play(ReplacementTransform(vel_plain, vel_live))
        vel_live.add_updater(update_vel_live)
        self.play(Indicate(vel_live[1], color=YELLOW))
        for target, run_time in [(3, 2.5), (0.1, 3), (1, 2)]:
            self.play(k.animate.set_value(target), run_time=run_time, rate_func=smooth)
            self.wait(0.4)
        self.play(k.animate.set_value(np.log(2)), run_time=2, rate_func=smooth)
        # the value of k is explained on a second line inside the red box
        def k_note_box(tex):
            note = MathTex(tex, color=bot_color, font_size=34).next_to(vel_live, DOWN, buff=0.15)
            return note, SurroundingRectangle(VGroup(vel_live, note), color=bot_color, buff=0.2, corner_radius=0.1)

        k_note, note_box = k_note_box(r"0.69 \approx \ln(2)")
        self.play(Transform(vel_box, note_box), Write(k_note))
        self.play(Circumscribe(vel_box, color=YELLOW))
        self.wait(1)

        # ---- 3) Base 2: when y = 1, x = 2 ----
        roll_to(1)
        self.play(Circumscribe(x_read, color=YELLOW), x_read.animate.scale(1.3), run_time=1.5)
        self.play(x_read.animate.scale(1 / 1.3))

        eq_center = np.array([1.35, -0.15, 0])

        def colored_tex(*parts, font_size=40):
            tex = MathTex(*[p for p, _ in parts], font_size=font_size)
            for sub, (_, color) in zip(tex, parts):
                sub.set_color(color)
            return tex

        def base_formulas(b):
            title = MathTex(r"\text{base } " + b + r"\,:", font_size=40)
            generic = colored_tex((r"\log_{" + b + "}(", WHITE), ("x", bot_color), (")", WHITE), ("=", WHITE),
                                  ("y", top_color))
            arrow = MathTex(r"\longrightarrow", font_size=40)
            return title, generic, arrow

        def live_formula(b, x_value, y_value):
            return VGroup(MathTex(r"\log_{" + b + "}(", font_size=40), number(x_value, bot_color, 40),
                          MathTex(")", font_size=40), MathTex("=", font_size=40), number(y_value, top_color, 40))

        def arrange_live(m):
            m.arrange(RIGHT, buff=0.08)
            m[3].shift(RIGHT * 0.06)
            m[4].shift(RIGHT * 0.12)

        def make_layout(b):
            title, generic, arrow = base_formulas(b)
            widest = live_formula(b, 1000, -3)
            arrange_live(widest)
            layout = VGroup(title, generic, arrow, widest).arrange(RIGHT, buff=0.3).move_to(eq_center)
            return layout

        live_anchor = VectorizedPoint()

        def update_live(m):
            set_x_value(m[1], red_x())
            m[4].set_value(t.get_value())
            arrange_live(m)
            m.move_to(live_anchor.get_center())

        layout = make_layout("2")
        title, generic, to_live = base_formulas("2")
        for mob, slot in zip([title, generic, to_live], layout):
            mob.move_to(slot)
        live_anchor.move_to(layout[3])
        self.add(live_anchor)
        live = live_formula("2", 2, 1)
        update_live(live)
        eq_box = SurroundingRectangle(layout, color=WHITE, buff=0.25, corner_radius=0.1)
        self.play(Create(eq_box), Write(title), run_time=1.2)
        self.play(Write(generic))
        self.play(Write(to_live), FadeIn(live, shift=LEFT * 0.3))
        live.add_updater(update_live)
        self.play(Circumscribe(VGroup(title, generic), color=YELLOW))
        self.wait(0.5)

        # The balls move on: stops (with wiggles) at y = 2 and y = 3, then back to the start
        for y_stop in [2, 3]:
            roll_to(y_stop)
            wiggle_values(y_read, x_read, live)
            self.wait(0.5)
        roll_to(0)
        self.wait(0.5)

        # ---- 4) Base 10: k becomes ln(10) ----
        self.play(Circumscribe(vel_box, color=YELLOW), FadeOut(k_note))
        self.play(k.animate.set_value(np.log(10)), run_time=2.5, rate_func=smooth)
        k_note, note_box = k_note_box(r"2.30 \approx \ln(10)")
        self.play(Transform(vel_box, note_box), Write(k_note))

        layout10 = make_layout("10")
        title10, generic10, to_live10 = base_formulas("10")
        for mob, slot in zip([title10, generic10, to_live10], layout10):
            mob.move_to(slot)
        live.clear_updaters()
        live10 = live_formula("10", 1, 0)
        self.play(live_anchor.animate.move_to(layout10[3]), run_time=0.01)
        update_live(live10)
        self.play(ReplacementTransform(title, title10), ReplacementTransform(generic, generic10),
                  to_live.animate.move_to(layout10[2]), ReplacementTransform(live, live10),
                  Transform(eq_box, SurroundingRectangle(layout10, color=WHITE, buff=0.25, corner_radius=0.1)),
                  run_time=2)
        live10.add_updater(update_live)
        self.play(Circumscribe(VGroup(title10, generic10), color=YELLOW))

        roll_to(1)
        self.play(Circumscribe(x_read, color=YELLOW))
        wiggle_values(y_read, x_read, live10)
        self.wait(0.5)
        roll_to(0)
        self.wait(0.5)

        # ---- 5) Negative values: the top axis turns into -7..4 ----
        self.play(morph.animate.set_value(1), run_time=3, rate_func=smooth)
        self.wait(0.5)
        # going down the red axis zooms in between 0 and 1: x = 0.1, 0.01, 0.001
        for y_stop in [-1, -2, -3]:
            roll_to(y_stop)
            wiggle_values(y_read, x_read, live10)
            self.wait(0.5)
        roll_to(0)                                  # no stops on the way back
        self.wait(1)

        # ---- 6) Towards 1000: the red axis zooms out (as in RollingBall8) ----
        for y_stop in [2, 3]:
            roll_to(y_stop)
            wiggle_values(y_read, x_read, live10)
            self.wait(0.5)
        self.wait(3)
