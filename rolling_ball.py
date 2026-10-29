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


class RollingBall4(Scene):
    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 8]            # pause when the bottom ball reaches these graduations
        x_end = 10                  # bottom ball stops at this graduation
        pause = 2.5                 # seconds of each pause
        top_color, bot_color = BLUE, RED

        # Two graduated axes from 0 (1 graduation = 1 scene unit), each ending in a dotted line
        def make_axis(y):
            axis = NumberLine(
                x_range=[0, 12, 1], length=12,
                include_numbers=True, font_size=26, color=GREY_B,
            )
            axis.shift(np.array([-6, y, 0]) - axis.n2p(0))   # graduation 0 at (-6, y)
            dots = DashedLine(axis.n2p(12), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            return axis, dots

        top_axis, top_dots = make_axis(2.4)
        bot_axis, bot_dots = make_axis(-1.4)

        # Point P at graduation 0 of the bottom axis
        p_dot = Dot(bot_axis.n2p(0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)

        # Green stars marking the starting positions
        stars = VGroup(
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(top_axis.n2p(0)),
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(bot_axis.n2p(1)),
        )

        # Top ball: starts at 0, constant velocity v = 1   ->  y(t) = t
        # Bottom ball: starts at 1, velocity v = x         ->  x(t) = e^t
        # so at every instant y = ln(x)
        top_pos = lambda s: s
        bot_pos = np.exp
        top_ball, top_spin = beach_ball(top_axis.n2p(0) + UP * r, r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(bot_axis.n2p(1) + UP * r, r, (bot_color, WHITE))

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

        top_ball.add_updater(rolling(top_axis, top_spin, top_pos))
        bot_ball.add_updater(rolling(bot_axis, bot_spin, bot_pos))

        # Small arrow under each ball (below the axis numbers), with the current position under it
        def position_marker(axis, position, name, color):
            arrow = Arrow(DOWN * 0.35, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.4)
            readout = VGroup(MathTex(name + " =", color=color, font_size=34),
                             DecimalNumber(0, num_decimal_places=2, color=color, font_size=34))

            def follow(mob):
                x = position(t.get_value())
                arrow.next_to(axis.n2p(x), DOWN, buff=0.6)
                readout[1].set_value(x)
                readout.arrange(RIGHT, buff=0.15).next_to(arrow, DOWN, buff=0.1)

            marker = VGroup(arrow, readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, readout

        top_marker, _ = position_marker(top_axis, top_pos, "y", top_color)
        bot_marker, bot_readout = position_marker(bot_axis, bot_pos, "x", bot_color)

        # Box between the axes with the instantaneous velocity of the bottom ball (v = x)
        v_label = MathTex("v =", color=bot_color)
        v_value = DecimalNumber(1, num_decimal_places=2, color=bot_color)
        v_value.add_updater(lambda m: m.set_value(bot_pos(t.get_value())))
        v_display = VGroup(v_label, v_value)
        v_display.add_updater(lambda m: m.arrange(RIGHT, buff=0.2).move_to(UP * 0.35))
        # Fixed-size box, sized for the widest value shown ("v = 10.00")
        widest = VGroup(MathTex("v ="), DecimalNumber(10)).arrange(RIGHT, buff=0.2)
        v_box = SurroundingRectangle(widest, color=bot_color, buff=0.25, corner_radius=0.1)
        v_box.move_to(UP * 0.35)

        self.add(top_axis, top_dots, bot_axis, bot_dots, p_dot, p_label, stars,
                 top_ball, bot_ball, top_marker, bot_marker, v_box, v_display)
        self.wait(0.5)

        # Roll, pausing at each x in x_stops to show that the velocity equals x
        for x_target in x_stops + [x_end]:
            t_target = np.log(x_target)
            self.play(t.animate.set_value(t_target),
                      run_time=t_target - t.get_value(), rate_func=linear)
            if x_target in x_stops:
                self.play(Indicate(v_display, color=YELLOW), Indicate(bot_readout, color=YELLOW))
                self.wait(pause - 1)

        self.wait(0.5)


class RollingBall5(Scene):
    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 8]            # pause when the bottom ball reaches these graduations
        x_end = 12                  # bottom ball stops at this graduation
        pause = 2.5                 # seconds of each pause
        top_color, bot_color = BLUE, RED

        # Two graduated axes from 0 (1 graduation = 1 scene unit), each ending in a dotted line
        def make_axis(y):
            axis = NumberLine(
                x_range=[0, 12, 1], length=12,
                include_numbers=True, font_size=26, color=GREY_B,
            )
            axis.shift(np.array([-6.5, y, 0]) - axis.n2p(0))   # graduation 0 at (-6.5, y)
            dots = DashedLine(axis.n2p(12), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            return axis, dots

        top_axis, top_dots = make_axis(2.2)
        bot_axis, bot_dots = make_axis(-1.75)

        # Point P at graduation 0 of the bottom axis
        p_dot = Dot(bot_axis.n2p(0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)

        # Green stars marking the starting positions
        stars = VGroup(
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(top_axis.n2p(0)),
            Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(bot_axis.n2p(1)),
        )

        # Top ball: starts at 0, constant velocity v = 1   ->  y(t) = t
        # Bottom ball: starts at 1, velocity v = x         ->  x(t) = e^t
        # so at every instant y = ln(x)
        top_pos = lambda s: s
        bot_pos = np.exp
        top_ball, top_spin = beach_ball(top_axis.n2p(0) + UP * r, r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(bot_axis.n2p(1) + UP * r, r, (bot_color, WHITE))

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

        top_ball.add_updater(rolling(top_axis, top_spin, top_pos))
        bot_ball.add_updater(rolling(bot_axis, bot_spin, bot_pos))

        # Arrow under each ball, its tip just below the axis, with the current position
        # and the current velocity written under it. The arrow leans to the right
        # so it doesn't cover the axis number under the ball
        def position_marker(axis, position, velocity, name, color):
            arrow = Arrow(RIGHT * 1.3 + DOWN * 0.87, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)

            def readout(symbol):
                return VGroup(MathTex(symbol + " =", color=color, font_size=34),
                              DecimalNumber(0, num_decimal_places=2, color=color, font_size=34))

            pos_readout, vel_readout = readout(name), readout("v")

            def follow(mob):
                s = t.get_value()
                arrow.shift(axis.n2p(position(s)) + DOWN * 0.08 - arrow.get_end())
                pos_readout[1].set_value(position(s))
                vel_readout[1].set_value(velocity(s))
                pos_readout.arrange(RIGHT, buff=0.15).next_to(arrow, DOWN, buff=0.1)
                vel_readout.arrange(RIGHT, buff=0.15).next_to(pos_readout, DOWN, buff=0.15)
                # keep the readouts inside the frame near the right edge
                overflow = VGroup(pos_readout, vel_readout).get_right()[0] - (config.frame_x_radius - 0.15)
                if overflow > 0:
                    pos_readout.shift(LEFT * overflow)
                    vel_readout.shift(LEFT * overflow)

            marker = VGroup(arrow, pos_readout, vel_readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, pos_readout, vel_readout

        top_marker, _, _ = position_marker(top_axis, top_pos, lambda s: 1, "y", top_color)
        bot_marker, bot_readout, bot_vel_readout = position_marker(bot_axis, bot_pos, np.exp, "x", bot_color)

        # 1) Time box in the upper left corner (t = y, the top ball's position)
        t_display = VGroup(MathTex("t =", font_size=40), DecimalNumber(0, num_decimal_places=2, font_size=40))
        t_display[1].add_updater(lambda m: m.set_value(t.get_value()))
        t_widest = VGroup(MathTex("t =", font_size=40), DecimalNumber(10, font_size=40)).arrange(RIGHT, buff=0.2)
        t_box = SurroundingRectangle(t_widest, color=WHITE, buff=0.15, corner_radius=0.1)
        t_box.to_corner(UL, buff=0.25)
        t_display.add_updater(lambda m: m.arrange(RIGHT, buff=0.2).move_to(t_box))

        self.add(top_axis, top_dots, bot_axis, bot_dots, p_dot, p_label, stars,
                 top_ball, bot_ball, top_marker, bot_marker, t_box, t_display)
        self.wait(0.5)

        # Roll, pausing at each x in x_stops to show that the velocity equals x
        for x_target in x_stops + [x_end]:
            t_target = np.log(x_target)
            self.play(t.animate.set_value(t_target),
                      run_time=t_target - t.get_value(), rate_func=linear)
            if x_target in x_stops:
                self.play(Indicate(bot_readout, color=YELLOW), Indicate(bot_vel_readout, color=YELLOW))
                self.wait(pause - 1)

        self.wait(0.5)
