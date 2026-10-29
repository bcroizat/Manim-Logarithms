from manim import *

class RollingBall(Scene):
    def construct(self):
        r = 0.4              # ball radius
        a = 1.5              # acceleration (speed increases by a per second)
        duration = 4         # seconds of motion

        # Horizontal axis with tick marks (they help you see the speed)
        axis = NumberLine(x_range=[-6.5, 6.5, 1], length=13,
                          include_numbers=False, color=GREY)
        axis.shift(DOWN)

        # Ball = filled circle + a radius line to make the rotation visible
        circle = Circle(radius=r, color=BLUE, fill_opacity=0.8)
        spoke = Line(circle.get_center(), circle.get_center() + UP * r, color=WHITE)
        ball = VGroup(circle, spoke)
        ball.move_to(axis.n2p(-6) + UP * r)

        ball.elapsed = 0

        def roll(mob, dt):
            mob.elapsed += dt
            dx = a * mob.elapsed * dt          # speed v = a*t, distance = v*dt
            mob.shift(RIGHT * dx)
            mob.rotate(-dx / r)                # rolling without slipping

        self.add(axis, ball)
        self.wait(0.5)
        ball.add_updater(roll)
        self.wait(duration)
        ball.remove_updater(roll)
        self.wait(0.5)
        
        
        
class RollingBall2(Scene):
    def construct(self):
        r = 0.4          # ball radius
        v0 = 1.0         # initial velocity (graduations per second)
        a = 0.8          # acceleration
        duration = 4     # seconds of motion

        # Graduated axis: 1 graduation = 1 scene unit, from -1 to 12
        axis = NumberLine(
            x_range=[-1, 12, 1], length=13,
            include_numbers=True, font_size=26, color=GREY_B,
        )
        axis.shift(DOWN)

        # Point P at graduation 0
        p_dot = Dot(axis.n2p(0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)

        # Ball starts at graduation 1, resting on the axis
        c = axis.n2p(1) + UP * r

        # Rotating part: beach-ball sectors
        spin = VGroup(*[
            # AnnularSector with inner_radius=0 is a pie slice; unlike Sector(radius=...),
            # outer_radius is honoured by every manim version (older ones ignore radius=)
            AnnularSector(inner_radius=0, outer_radius=r,
                          start_angle=i * PI / 3, angle=PI / 3,
                          fill_color=RED if i % 2 == 0 else WHITE,
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
        ### dark_side = Difference(
        #    Circle(radius=r), Circle(radius=r).shift(light_dir * r * 0.3),
        #    fill_color=BLACK, fill_opacity=0.3, stroke_width=0,
        #).move_to(c - light_dir * r * 0.06)
        #outline = Circle(radius=r, stroke_color=BLACK, stroke_width=1.5, stroke_opacity=0.5).move_to(c)

        dark_side = Difference(
            Circle(radius=r).move_to(c),
            Circle(radius=r).move_to(c + light_dir * r * 0.3),
            fill_color=BLACK, fill_opacity=0.3, stroke_width=0,
        )
        
        outline = Circle(radius=r, stroke_color=BLACK, stroke_width=2.5, stroke_opacity=0.8).move_to(c)
        # Shadow on the axis
        shadow = Ellipse(width=r * 1.8, height=0.1).set_fill(BLACK, opacity=0.5).set_stroke(width=0)
        shadow.move_to(axis.n2p(1) + DOWN * 0.02)

        lighting = VGroup(shade, highlight, dark_side, outline)
        ball = VGroup(shadow, spin, lighting)

        state = {"t": 0.0, "pos": c.copy()}

        def roll(mob, dt):
            v = v0 + a * (state["t"] + dt / 2)    # mean speed over this frame
            dx = v * dt
            state["t"] += dt
            # whole ball moves, but only the sectors rotate
            mob.shift(RIGHT * dx)
            state["pos"] = state["pos"] + RIGHT * dx
            spin.rotate(-dx / r, about_point=state["pos"])

        self.add(axis, p_dot, p_label, ball)
        ball.add_updater(roll)
        self.wait(duration)
        ball.remove_updater(roll)
        self.wait(0.5)


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


class RollingBall3(Scene):
    def construct(self):
        r = 0.4                 # ball radius
        x_end = 10              # bottom ball stops at this graduation
        duration = np.log(x_end)  # x = e^t reaches x_end at t = ln(x_end)

        # Two graduated axes (1 graduation = 1 scene unit), each ending in a dotted line
        def make_axis(y):
            axis = NumberLine(
                x_range=[-1, 11, 1], length=12,
                include_numbers=True, font_size=26, color=GREY_B,
            )
            axis.shift(np.array([-6.5, y, 0]) - axis.n2p(-1))   # graduation -1 at (-6.5, y)
            dots = DashedLine(axis.n2p(11), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            return axis, dots

        top_axis, top_dots = make_axis(1.5)
        bot_axis, bot_dots = make_axis(-1.5)

        # Point P at graduation 0 of each axis
        p_marks = VGroup()
        for axis in (top_axis, bot_axis):
            p_dot = Dot(axis.n2p(0), color=YELLOW, radius=0.08)
            p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)
            p_marks.add(p_dot, p_label)

        # Top ball: starts at 0, constant velocity v = 1   ->  y(t) = t
        # Bottom ball: starts at 1, velocity v = x         ->  x(t) = e^t
        # so at every instant y = ln(x)
        top_ball, top_spin = beach_ball(top_axis.n2p(0) + UP * r, r, (BLUE, YELLOW))
        bot_ball, bot_spin = beach_ball(bot_axis.n2p(1) + UP * r, r, (RED, WHITE))

        t = ValueTracker(0)

        def rolling(axis, spin, position):
            # Positions come from the exact formula, so there is no accumulated drift
            state = {"x": position(0)}

            def roll(mob, dt):
                x = position(t.get_value())
                dx = x - state["x"]
                state["x"] = x
                mob.shift(RIGHT * dx)
                spin.rotate(-dx / r, about_point=axis.n2p(x) + UP * r)   # rolling without slipping
            return roll

        top_ball.add_updater(rolling(top_axis, top_spin, lambda s: s))
        bot_ball.add_updater(rolling(bot_axis, bot_spin, np.exp))

        self.add(top_axis, top_dots, bot_axis, bot_dots, p_marks, top_ball, bot_ball)
        self.wait(0.5)
        self.play(t.animate.set_value(duration), run_time=duration, rate_func=linear)
        top_ball.clear_updaters()
        bot_ball.clear_updaters()
        self.wait(0.5)
