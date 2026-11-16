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
    # Which ball (with its axis and readouts) is shown; the subclasses below turn one off
    show_top = True
    show_bot = True
    t_end = 7                   # the animation runs until t = t_end (the red ball rolls off screen)
    slow_motion = 2             # 1 = normal speed, 2 = twice as slow, 3 = three times as slow...
    finale = False              # True: quick rewind to t = 0, then a run without stops while the
    finale_x = 1000             # red axis zooms out, until the red ball reaches finale_x

    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 7.389, 10]    # pause when the bottom ball reaches these graduations
        pause = 3.5                 # seconds of each pause
        slow_motion = self.slow_motion
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

        # Screen units per graduation on the red axis: 1, except during the finale where, beyond
        # x_zoom, the axis zooms out so that the red ball stays at the screen position of x_zoom
        x_zoom = 11
        zoom = {"on": False}

        def bot_unit():
            x = bot_pos(t.get_value())
            return x_zoom / x if zoom["on"] and x > x_zoom else 1

        def top_point(v):
            return top_axis.n2p(v)

        def bot_point(v):
            return bot_axis.n2p(0) + RIGHT * v * bot_unit()

        def rolling(to_point, spin, position, unit=lambda: 1):
            # Positions come from the exact formula, so there is no accumulated drift; the ball
            # turns by the distance rolled at the current scale (rolling without slipping)
            state = {"x": position(0), "screen": to_point(position(0))[0]}

            def roll(mob, dt):
                x = position(t.get_value())
                screen = to_point(x)[0]
                mob.shift(RIGHT * (screen - state["screen"]))
                spin.rotate(-(x - state["x"]) * unit() / r, about_point=spin.get_center())
                state["x"], state["screen"] = x, screen
            return roll

        top_ball.add_updater(rolling(top_point, top_spin, top_pos))
        bot_ball.add_updater(rolling(bot_point, bot_spin, bot_pos, bot_unit))

        # Arrow under each ball, its tip just below the axis, with the current position
        # and the current velocity written under it. The arrow leans to the right
        # so it doesn't cover the axis number under the ball
        def position_marker(axis, to_point, position, velocity, name, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)

            def readout(symbol):
                return VGroup(MathTex(symbol + " =", color=color, font_size=34),
                              DecimalNumber(0, num_decimal_places=2, color=color, font_size=34,
                                            group_with_commas=False))

            pos_readout, vel_readout = readout(name), readout("v")

            def follow(mob):
                s = t.get_value()
                arrow.shift(to_point(position(s)) + DOWN * 0.08 - arrow.get_end())
                pos_readout[1].set_value(position(s))
                vel_readout[1].set_value(velocity(s))
                pos_readout.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)
                vel_readout.arrange(RIGHT, buff=0.15).next_to(pos_readout, DOWN, buff=0.15)
                # keep the readouts inside the frame near the right edge; past the end of the
                # axis they follow the ball again, so they leave the screen together with it
                overflow = VGroup(pos_readout, vel_readout).get_right()[0] - (config.frame_x_radius - 0.15)
                overflow -= max(0, arrow.get_end()[0] - axis.n2p(12)[0])
                if overflow > 0:
                    pos_readout.shift(LEFT * overflow)
                    vel_readout.shift(LEFT * overflow)

            marker = VGroup(arrow, pos_readout, vel_readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, pos_readout, vel_readout

        top_marker, top_readout, top_vel_readout = position_marker(top_axis, top_point, top_pos, lambda s: 1,
                                                                   "y", top_color)
        bot_marker, bot_readout, bot_vel_readout = position_marker(bot_axis, bot_point, bot_pos, np.exp,
                                                                   "x", bot_color)

        # 1) Time box in the upper left corner (t = y, the top ball's position)
        t_display = VGroup(MathTex("t =", font_size=40), DecimalNumber(0, num_decimal_places=2, font_size=40))
        t_display[1].add_updater(lambda m: m.set_value(t.get_value()))
        t_widest = VGroup(MathTex("t =", font_size=40), DecimalNumber(10, font_size=40)).arrange(RIGHT, buff=0.2)
        t_box = SurroundingRectangle(t_widest, color=WHITE, buff=0.15, corner_radius=0.1)
        t_box.to_corner(UL, buff=0.25)
        t_display.add_updater(lambda m: m.arrange(RIGHT, buff=0.2).move_to(t_box))

        if self.show_top:
            self.add(top_axis, top_dots, stars[0], top_ball, top_marker)
        if self.show_bot:
            self.add(bot_axis, bot_dots, p_dot, p_label, stars[1], bot_ball, bot_marker)
        self.add(t_box, t_display)
        self.wait(1.5)

        # Roll, pausing when the bottom ball reaches each x in x_stops (at t = ln x)
        # to show that its velocity equals x, then carry on until t = t_end
        stops = [np.log(x) for x in x_stops]
        for t_target in stops + [self.t_end]:
            self.play(t.animate.set_value(t_target),
                      run_time=(t_target - t.get_value()) * slow_motion, rate_func=linear)
            if t_target in stops:
                # highlight the bottom (red) values first, then the top (blue) ones;
                # a hidden ball's highlight becomes a wait so all versions keep the same timing
                if self.show_bot:
                    self.play(Indicate(bot_readout, color=YELLOW), Indicate(bot_vel_readout, color=YELLOW))
                else:
                    self.wait(1)
                if self.show_top:
                    self.play(Indicate(top_readout, color=YELLOW), Indicate(top_vel_readout, color=YELLOW))
                else:
                    self.wait(1)
                self.wait(pause - 2)

        if self.finale and self.show_bot:
            # Quick rewind to the start
            self.play(t.animate.set_value(0), run_time=2, rate_func=smooth)

            # The red axis' graduations are swapped for zoomable ones (identical at scale 1):
            # a fixed set of ticks and numbers, renumbered every 1, 2, 5, 10, ... graduations
            steps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
            minor_steps = {1: None, 2: 1, 5: 1, 10: 2, 20: 10, 50: 10, 100: 20, 200: 100, 500: 100, 1000: 200}
            min_gap = 0.75                  # minimum screen distance between two numbers
            ticks = VGroup(*[Line(DOWN * 0.1, UP * 0.1, color=GREY_B, stroke_width=2)
                             for _ in range(int(12 / (min_gap / 5)) + 2)])
            numbers = VGroup(*[Integer(0, font_size=26, group_with_commas=False)
                               for _ in range(int(12 / min_gap) + 2)])
            shown = [None] * len(numbers)

            def draw_graduations(group):
                u = bot_unit()
                step = next(n for n in steps if n * u >= min_gap)
                minor = minor_steps[step] or step
                last = 12 / u + 1e-9                    # end of the solid line
                tick_values = np.arange(0, last, minor)
                for tick, v in zip(ticks, tick_values):
                    p = bot_point(v)
                    h = 0.1 if v % step == 0 else 0.05
                    tick.put_start_and_end_on(p + DOWN * h, p + UP * h).set_stroke(opacity=1)
                for tick in ticks[len(tick_values):]:
                    tick.set_stroke(opacity=0)
                number_values = np.arange(0, last, step)
                for i, num in enumerate(numbers):
                    if i < len(number_values):
                        v = int(number_values[i])
                        if shown[i] != v:
                            num.set_value(v)
                            shown[i] = v
                        num.next_to(bot_point(v), DOWN, buff=0.25).set_opacity(1)
                    else:
                        num.set_opacity(0)

            graduations = VGroup(ticks, numbers)
            draw_graduations(graduations)
            graduations.add_updater(draw_graduations)
            line = Line(bot_axis.n2p(0), bot_axis.n2p(12), color=GREY_B, stroke_width=2)
            self.remove(bot_axis)
            self.add(line, graduations)
            self.bring_to_front(p_dot, p_label, stars[1], bot_ball, bot_marker)
            stars[1].add_updater(lambda m: m.move_to(bot_point(1)))
            zoom["on"] = True

            # Off again, without stops, until the red ball reaches finale_x
            t_final = np.log(self.finale_x)
            self.play(t.animate.set_value(t_final), run_time=t_final * slow_motion, rate_func=linear)

        self.wait(1.5)


class RollingBall5Bottom(RollingBall5):
    # Only the bottom axis and the red ball (v = x), a little slower: first up to t = 3
    # (with the usual stops), then a quick rewind and a run up to x = 1000 with a zoom-out
    show_top = False
    t_end = 3
    slow_motion = 2.5
    finale = True


class RollingBall5Top(RollingBall5):
    # Only the top axis and the blue ball (v = 1)
    show_bot = False
    #t_end = np.log(12)          # stops when the (hidden) red ball would reach 12
    t_end = 7

class RollingBall6(Scene):
    t_end = 3                   # the animation runs until t = t_end (the red ball rolls off screen)

    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 7.389, 10]    # pause when the bottom ball reaches these graduations
        pause = 3.5                 # seconds of each pause
        slow_motion = 2             # 1 = normal speed, 2 = twice as slow, 3 = three times as slow...
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
        # written under its tail. The arrow leans to the right so it doesn't cover the
        # axis number under the ball
        def position_marker(axis, position, name, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            readout = VGroup(MathTex(name + " =", color=color, font_size=34),
                             DecimalNumber(0, num_decimal_places=2, color=color, font_size=34))

            def follow(mob):
                s = t.get_value()
                arrow.shift(axis.n2p(position(s)) + DOWN * 0.08 - arrow.get_end())
                readout[1].set_value(position(s))
                readout.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)
                # keep the readout inside the frame near the right edge; past the end of the
                # axis it follows the ball again, so it leaves the screen together with it
                overflow = readout.get_right()[0] - (config.frame_x_radius - 0.15)
                overflow -= max(0, arrow.get_end()[0] - axis.n2p(12)[0])
                if overflow > 0:
                    readout.shift(LEFT * overflow)

            marker = VGroup(arrow, readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, readout

        top_marker, top_readout = position_marker(top_axis, top_pos, "y", top_color)
        bot_marker, bot_readout = position_marker(bot_axis, bot_pos, "x", bot_color)

        # Box between the axes: ln(x) = y, with x in red and y in blue
        def equation(x_value, y_value):
            return VGroup(
                MathTex(r"\ln("),
                DecimalNumber(x_value, num_decimal_places=2, color=bot_color),
                MathTex(")"),
                MathTex("="),
                DecimalNumber(y_value, num_decimal_places=2, color=top_color),
            )

        eq_center = UP * 0.15
        eq = equation(1, 0)

        def update_eq(m):
            s = t.get_value()
            m[1].set_value(bot_pos(s))
            m[4].set_value(top_pos(s))
            m.arrange(RIGHT, buff=0.12).move_to(eq_center)
            m[3].shift(RIGHT * 0.06)                # a little more room around "="
            m[4].shift(RIGHT * 0.12)

        update_eq(eq)
        eq.add_updater(update_eq)
        # Fixed-size box, sized for the widest equation shown ("ln(20.09) = 3.00")
        widest = equation(20.09, 3).arrange(RIGHT, buff=0.12)
        eq_box = SurroundingRectangle(widest, color=WHITE, buff=0.3, corner_radius=0.1)
        eq_box.stretch_to_fit_width(eq_box.width + 0.2).move_to(eq_center)

        self.add(top_axis, top_dots, stars[0], top_ball, top_marker,
                 bot_axis, bot_dots, p_dot, p_label, stars[1], bot_ball, bot_marker,
                 eq_box, eq)
        self.wait(1.5)

        # Roll, pausing when the bottom ball reaches each x in x_stops (at t = ln x),
        # then carry on until t = t_end
        stops = [np.log(x) for x in x_stops]
        for t_target in stops + [self.t_end]:
            self.play(t.animate.set_value(t_target),
                      run_time=(t_target - t.get_value()) * slow_motion, rate_func=linear)
            if t_target in stops:
                # highlight the bottom (red) value first, then the top (blue) one
                self.play(Indicate(bot_readout, color=YELLOW))
                self.play(Indicate(top_readout, color=YELLOW))
                self.wait(pause - 2)

        self.wait(1.5)


class RollingBall7(Scene):
    t_end = 4                   # the animation runs until t = t_end
    x_zoom = 11                 # once the red ball passes this graduation, the axes zoom out

    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 7.389, 10]    # pause when the bottom ball reaches these graduations
        pause = 3.5                 # seconds of each pause
        slow_motion = 2             # 1 = normal speed, 2 = twice as slow, 3 = three times as slow...
        top_color, bot_color = BLUE, RED
        x0 = -6.5                   # screen position of graduation 0
        axis_length = 12            # screen length of the solid part of each axis

        t = ValueTracker(0)

        # Top ball: starts at 0, constant velocity v = 1   ->  y(t) = t
        # Bottom ball: starts at 1, velocity v = x         ->  x(t) = e^t
        # so at every instant y = ln(x)
        top_pos = lambda s: s
        bot_pos = np.exp

        # Zoom: screen units per graduation. It is 1 until the red ball reaches x_zoom,
        # then shrinks so that the red ball stays at the screen position of x_zoom
        def unit(s):
            return min(1, self.x_zoom / bot_pos(s))

        def to_screen(k, y, s):
            return np.array([x0 + k * unit(s), y, 0])

        # Graduated axis from 0 whose graduations squeeze together as we zoom out.
        # The solid line and the dotted end stay put; ticks and numbers are moved each frame.
        # (All ticks and numbers exist from the start and are only shown or hidden: manim
        # does not draw objects added to the scene in the middle of an animation.)
        k_max = int(axis_length / unit(self.t_end)) + 1     # highest graduation ever visible

        def make_axis(y):
            line = Line(np.array([x0, y, 0]), np.array([x0 + axis_length, y, 0]),
                        color=GREY_B, stroke_width=2)
            dots = DashedLine(line.get_end(), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            ticks = VGroup(*[Line(DOWN * 0.1, UP * 0.1, color=GREY_B, stroke_width=2)
                             for k in range(k_max + 1)])
            numbers = VGroup(*[MathTex(str(k), font_size=26) for k in range(k_max + 1)])

            def draw_ticks(m):
                s = t.get_value()
                u = unit(s)
                # numbered step: 1, 2, 5, 10... whichever keeps the numbers apart
                step = next(n for n in (1, 2, 5, 10, 20, 50, 100) if n * u >= 0.6)
                k_last = int(axis_length / u + 1e-9)        # last graduation on the solid line
                for k in range(k_max + 1):
                    p = to_screen(k, y, s)
                    numbered = k % step == 0
                    h = 0.1 if numbered else 0.05           # small unlabelled ticks in between
                    ticks[k].put_start_and_end_on(p + DOWN * h, p + UP * h)
                    ticks[k].set_stroke(opacity=1 if k <= k_last else 0)
                    numbers[k].next_to(p, DOWN, buff=0.25)
                    numbers[k].set_opacity(1 if numbered and k <= k_last else 0)

            graduations = VGroup(ticks, numbers)
            draw_ticks(graduations)
            graduations.add_updater(draw_ticks)
            return VGroup(line, dots, graduations)

        top_y, bot_y = 2.2, -1.75
        top_axis, bot_axis = make_axis(top_y), make_axis(bot_y)

        # Point P at graduation 0 of the bottom axis
        p_dot = Dot(to_screen(0, bot_y, 0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)

        # Green stars marking the starting positions (they follow the zoom)
        top_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(to_screen(0, top_y, 0))
        bot_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1)
        bot_star.add_updater(lambda m: m.move_to(to_screen(1, bot_y, t.get_value())))

        top_ball, top_spin = beach_ball(to_screen(0, top_y, 0) + UP * r, r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(to_screen(1, bot_y, 0) + UP * r, r, (bot_color, WHITE))

        def rolling(y, spin, position):
            # Positions come from the exact formula, so there is no accumulated drift
            state = {"pos": position(0), "screen_x": to_screen(position(0), y, 0)[0]}

            def roll(mob, dt):
                s = t.get_value()
                pos = position(s)
                screen_x = to_screen(pos, y, s)[0]
                mob.shift(RIGHT * (screen_x - state["screen_x"]))
                # rolling without slipping on the axis at its current scale
                spin.rotate(-(pos - state["pos"]) * unit(s) / r, about_point=np.array([screen_x, y + r, 0]))
                state["pos"], state["screen_x"] = pos, screen_x
            return roll

        top_ball.add_updater(rolling(top_y, top_spin, top_pos))
        bot_ball.add_updater(rolling(bot_y, bot_spin, bot_pos))

        # Arrow under each ball, its tip just below the axis, with the current position
        # written under its tail. The arrow leans to the right so it doesn't cover the
        # axis number under the ball
        def position_marker(y, position, name, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            readout = VGroup(MathTex(name + " =", color=color, font_size=34),
                             DecimalNumber(0, num_decimal_places=2, color=color, font_size=34))

            def follow(mob):
                s = t.get_value()
                arrow.shift(to_screen(position(s), y, s) + DOWN * 0.08 - arrow.get_end())
                readout[1].set_value(position(s))
                readout.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)

            marker = VGroup(arrow, readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, readout

        top_marker, top_readout = position_marker(top_y, top_pos, "y", top_color)
        bot_marker, bot_readout = position_marker(bot_y, bot_pos, "x", bot_color)

        # Box between the axes: ln(x) = y, with x in red and y in blue
        def equation(x_value, y_value):
            return VGroup(
                MathTex(r"\ln("),
                DecimalNumber(x_value, num_decimal_places=2, color=bot_color),
                MathTex(")"),
                MathTex("="),
                DecimalNumber(y_value, num_decimal_places=2, color=top_color),
            )

        eq_center = UP * 0.15
        eq = equation(1, 0)

        def update_eq(m):
            s = t.get_value()
            m[1].set_value(bot_pos(s))
            m[4].set_value(top_pos(s))
            m.arrange(RIGHT, buff=0.12).move_to(eq_center)
            m[3].shift(RIGHT * 0.06)                # a little more room around "="
            m[4].shift(RIGHT * 0.12)

        update_eq(eq)
        eq.add_updater(update_eq)
        # Fixed-size box, sized for the widest equation shown ("ln(54.60) = 4.00")
        widest = equation(54.6, 4).arrange(RIGHT, buff=0.12)
        eq_box = SurroundingRectangle(widest, color=WHITE, buff=0.3, corner_radius=0.1)
        eq_box.stretch_to_fit_width(eq_box.width + 0.2).move_to(eq_center)

        self.add(top_axis, top_star, top_ball, top_marker,
                 bot_axis, p_dot, p_label, bot_star, bot_ball, bot_marker,
                 eq_box, eq)
        self.wait(1.5)

        # Roll, pausing when the bottom ball reaches each x in x_stops (at t = ln x),
        # then carry on until t = t_end
        stops = [np.log(x) for x in x_stops]
        for t_target in stops + [self.t_end]:
            self.play(t.animate.set_value(t_target),
                      run_time=(t_target - t.get_value()) * slow_motion, rate_func=linear)
            if t_target in stops:
                # flash both red x values together, then both blue y values
                self.play(Indicate(bot_readout, color=YELLOW), Indicate(eq[1], color=YELLOW))
                self.play(Indicate(top_readout, color=YELLOW), Indicate(eq[4], color=YELLOW))
                self.wait(pause - 2)

        self.wait(1.5)


class RollingBall8(Scene):
    t_end = 7                   # the animation runs until t = t_end (x = e^7, about 1097)
    x_zoom = 11                 # once the red ball passes this graduation, the axes zoom out
    zoom_top = False            # False: only the bottom (red) axis zooms out

    def construct(self):
        r = 0.4                     # ball radius
        x_stops = [3, 7.389, 10, 100, 500]   # pause when the bottom ball reaches these graduations
        pause = 3.5                 # seconds of each pause
        slow_motion = 2             # 1 = normal speed, 2 = twice as slow, 3 = three times as slow...
        top_color, bot_color = BLUE, RED
        x0 = -6.5                   # screen position of graduation 0
        axis_length = 12            # screen length of the solid part of each axis

        t = ValueTracker(0)

        # Top ball: starts at 0, constant velocity v = 1   ->  y(t) = t
        # Bottom ball: starts at 1, velocity v = x         ->  x(t) = e^t
        # so at every instant y = ln(x)
        top_pos = lambda s: s
        bot_pos = np.exp

        top_y, bot_y = 2.2, -1.75

        # Zoom: screen units per graduation. It is 1 until the red ball reaches x_zoom,
        # then shrinks so that the red ball stays at the screen position of x_zoom
        def unit(s, y):
            if y == top_y and not self.zoom_top:
                return 1
            return min(1, self.x_zoom / bot_pos(s))

        def to_screen(k, y, s):
            return np.array([x0 + k * unit(s, y), y, 0])

        # Graduated axis from 0 whose graduations squeeze together as we zoom out.
        # The solid line and the dotted end stay put. A fixed set of ticks and numbers is
        # moved, renumbered, shown or hidden each frame (manim does not draw objects added
        # to the scene in the middle of an animation, so none are created or removed)
        steps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
        minor_steps = {1: None, 2: 1, 5: 1, 10: 2, 20: 10, 50: 10, 100: 20,
                       200: 100, 500: 100, 1000: 200, 2000: 1000, 5000: 1000}
        min_gap = 0.75              # minimum screen distance between two numbers
        n_numbers = int(axis_length / min_gap) + 2
        n_ticks = int(axis_length / (min_gap / 5)) + 2

        def make_axis(y):
            line = Line(np.array([x0, y, 0]), np.array([x0 + axis_length, y, 0]),
                        color=GREY_B, stroke_width=2)
            dots = DashedLine(line.get_end(), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            ticks = VGroup(*[Line(DOWN * 0.1, UP * 0.1, color=GREY_B, stroke_width=2)
                             for _ in range(n_ticks)])
            numbers = VGroup(*[Integer(0, font_size=26, group_with_commas=False) for _ in range(n_numbers)])
            shown = [0] * n_numbers         # value currently written on each number

            def draw_ticks(m):
                s = t.get_value()
                u = unit(s, y)
                step = next(n for n in steps if n * u >= min_gap)     # numbered graduations
                minor = minor_steps[step] or step                      # small ticks in between
                k_last = axis_length / u + 1e-9                        # end of the solid line
                tick_values = np.arange(0, k_last, minor)
                for tick, k in zip(ticks, tick_values):
                    p = to_screen(k, y, s)
                    h = 0.1 if k % step == 0 else 0.05
                    tick.put_start_and_end_on(p + DOWN * h, p + UP * h).set_stroke(opacity=1)
                for tick in ticks[len(tick_values):]:
                    tick.set_stroke(opacity=0)
                number_values = np.arange(0, k_last, step)
                for i, number in enumerate(numbers):
                    if i < len(number_values):
                        k = int(number_values[i])
                        if shown[i] != k:
                            number.set_value(k)
                            shown[i] = k
                        number.next_to(to_screen(k, y, s), DOWN, buff=0.25).set_opacity(1)
                    else:
                        number.set_opacity(0)

            graduations = VGroup(ticks, numbers)
            draw_ticks(graduations)
            graduations.add_updater(draw_ticks)
            return VGroup(line, dots, graduations)

        top_axis, bot_axis = make_axis(top_y), make_axis(bot_y)

        # Point P at graduation 0 of the bottom axis
        p_dot = Dot(to_screen(0, bot_y, 0), color=YELLOW, radius=0.08)
        p_label = MathTex("P", color=YELLOW).next_to(p_dot, UP, buff=0.2)

        # Green stars marking the starting positions (they follow the zoom)
        top_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(to_screen(0, top_y, 0))
        bot_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1)
        bot_star.add_updater(lambda m: m.move_to(to_screen(1, bot_y, t.get_value())))

        top_ball, top_spin = beach_ball(to_screen(0, top_y, 0) + UP * r, r, (top_color, YELLOW))
        bot_ball, bot_spin = beach_ball(to_screen(1, bot_y, 0) + UP * r, r, (bot_color, WHITE))

        # A small jump (used in the introduction): while hop goes from 0 to 1, the balls fly
        # over their axis along an arc and do not turn
        hop = ValueTracker(0)
        hop_height = 0.8

        def lift():
            p = hop.get_value()
            return hop_height * 4 * p * (1 - p) if 0 < p < 1 else 0

        def rolling(y, spin, position):
            # Positions come from the exact formula, so there is no accumulated drift
            state = {"pos": position(0), "screen_x": to_screen(position(0), y, 0)[0], "lift": 0}

            def roll(mob, dt):
                s = t.get_value()
                pos = position(s)
                screen_x = to_screen(pos, y, s)[0]
                height = lift()
                mob.shift(RIGHT * (screen_x - state["screen_x"]) + UP * (height - state["lift"]))
                # rolling without slipping on the axis at its current scale (not while in the air)
                if height == 0 and state["lift"] == 0:
                    spin.rotate(-(pos - state["pos"]) * unit(s, y) / r, about_point=spin.get_center())
                state["pos"], state["screen_x"], state["lift"] = pos, screen_x, height
            return roll

        top_ball.add_updater(rolling(top_y, top_spin, top_pos))
        bot_ball.add_updater(rolling(bot_y, bot_spin, bot_pos))

        # Arrow under each ball, its tip just below the axis, with the current position
        # written under its tail. The arrow leans to the right so it doesn't cover the
        # axis number under the ball
        def position_marker(y, position, name, color):
            arrow = Arrow(RIGHT * 0.7 + DOWN * 0.84, ORIGIN, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.1)
            readout = VGroup(MathTex(name + " =", color=color, font_size=34),
                             DecimalNumber(0, num_decimal_places=2, color=color, font_size=34,
                                           group_with_commas=False))

            def follow(mob):
                s = t.get_value()
                arrow.shift(to_screen(position(s), y, s) + DOWN * 0.08 - arrow.get_end())
                readout[1].set_value(position(s))
                readout.arrange(RIGHT, buff=0.15).next_to(arrow.get_start(), DOWN, buff=0.1)

            marker = VGroup(arrow, readout)
            follow(marker)
            marker.add_updater(follow)
            return marker, readout

        top_marker, top_readout = position_marker(top_y, top_pos, "y", top_color)
        bot_marker, bot_readout = position_marker(bot_y, bot_pos, "x", bot_color)

        # Box between the axes: ln(x) = y, with x in red and y in blue
        def equation(x_value, y_value):
            return VGroup(
                MathTex(r"\ln("),
                DecimalNumber(x_value, num_decimal_places=2, color=bot_color, group_with_commas=False),
                MathTex(")"),
                MathTex("="),
                DecimalNumber(y_value, num_decimal_places=2, color=top_color),
            )

        eq_center = UP * 0.15
        eq = equation(1, 0)

        def update_eq(m):
            s = t.get_value()
            m[1].set_value(bot_pos(s))
            m[4].set_value(top_pos(s))
            m.arrange(RIGHT, buff=0.12).move_to(eq_center)
            m[3].shift(RIGHT * 0.06)                # a little more room around "="
            m[4].shift(RIGHT * 0.12)

        update_eq(eq)
        # Fixed-size box, sized for the widest equation shown
        widest = equation(bot_pos(self.t_end), top_pos(self.t_end)).arrange(RIGHT, buff=0.12)
        eq_box = SurroundingRectangle(widest, color=WHITE, buff=0.3, corner_radius=0.1)
        eq_box.stretch_to_fit_width(eq_box.width + 0.2).move_to(eq_center)

        self.add(top_axis, top_star, top_ball, top_marker,
                 bot_axis, p_dot, p_label, bot_star, bot_ball, bot_marker)
        self.wait(1.5)

        # ---- Introduction: the "ln" arrow, a short run, a jump back, then ln(x) = y ----
        # A big arrow goes up from the red axis to the blue one: x -> y is the logarithm
        big_arrow = Arrow(np.array([6.2, bot_y + 0.35, 0]), np.array([6.2, top_y - 0.35, 0]), buff=0,
                          color=YELLOW, stroke_width=10, max_tip_length_to_length_ratio=0.15)
        arrow_name = MathTex(r"\ln", color=YELLOW, font_size=48).next_to(big_arrow, LEFT, buff=0.2)
        self.play(GrowArrow(big_arrow), Write(arrow_name), run_time=1.5)
        self.play(ShowPassingFlash(big_arrow.copy().set_color(WHITE), time_width=0.5),
                  Indicate(arrow_name, color=WHITE))

        # The balls roll a little (t = 0 to 1.5), then jump back to their starting positions
        self.play(t.animate.set_value(1.5), run_time=1.5 * slow_motion, rate_func=linear)
        self.wait(0.5)
        self.play(t.animate(rate_func=smooth).set_value(0), hop.animate(rate_func=linear).set_value(1),
                  run_time=1.5)
        self.wait(0.5)

        # Balls at rest: the box appears with ln(x) = y, then x and y become 1 and 0
        def symbolic(x_tex, y_tex):
            tex = MathTex(r"\ln(", x_tex, ")", "=", y_tex)
            tex[1].set_color(bot_color)
            tex[4].set_color(top_color)
            return tex.move_to(eq_center)

        letters, values = symbolic("x", "y"), symbolic("1", "0")
        self.play(FadeOut(big_arrow, shift=UP * 0.5), FadeOut(arrow_name, shift=UP * 0.5),
                  Create(eq_box), Write(letters), run_time=1.5)
        self.play(Circumscribe(letters, color=YELLOW))
        self.wait(0.5)
        self.play(ReplacementTransform(letters, values), run_time=1.5)
        self.play(Indicate(values[1], color=YELLOW), Indicate(values[4], color=YELLOW))
        self.wait(1)
        # then the live values take over and the video goes on as before
        self.play(ReplacementTransform(values, eq), run_time=0.8)
        eq.add_updater(update_eq)
        self.wait(0.5)

        # Roll, pausing when the bottom ball reaches each x in x_stops (at t = ln x),
        # then carry on until t = t_end
        stops = [np.log(x) for x in x_stops]
        for t_target in stops + [self.t_end]:
            self.play(t.animate.set_value(t_target),
                      run_time=(t_target - t.get_value()) * slow_motion, rate_func=linear)
            if t_target in stops:
                # flash both red x values together, then both blue y values
                self.play(Indicate(bot_readout, color=YELLOW), Indicate(eq[1], color=YELLOW))
                self.play(Indicate(top_readout, color=YELLOW), Indicate(eq[4], color=YELLOW))
                self.wait(pause - 2)

        self.wait(1.5)


# ====================== Neper's original construction (4 scenes) ======================
# The red ball now runs towards a fixed point P with a speed proportional to its remaining
# distance x to P (Neper's construction, x0 = 10^7), while the blue ball moves at constant
# speed: y = Nap.Log(x). On screen the motion is exaggerated so that it can be seen, but the
# values written in the boxes and the table are the true ones (x0 = 10^7).
#   NeperContinu : from the usual axes to Neper's segment, continuous motion, y = Nap.Log(x),
#                  and the product rule (first the naive one, then the corrected one)
#   NeperSauts   : Neper's discrete steps, Y_n = n Y_1 and X_n = X_0 q^n
#   NeperTable   : zoom out, the table (step, X_n, Y_n), then the numbers scroll by
#   NeperEtLn    : back to the continuous motion, y = Nap.Log(x) = -10^7 ln(x / 10^7)

NEPER_X0 = 10 ** 7
NEPER_Q = 1 - 1e-7              # Neper's ratio between two consecutive X
NEPER_Y1 = 1.00000005           # Neper's value of Nap.Log(9 999 999)


class NeperMixin:
    """Shared drawing for the Neper scenes (not a scene itself, so that manim -a skips it)."""
    r = 0.4                     # ball radius
    x0 = -6.5                   # screen position of graduation 0 (top axis)
    top_y, bot_y = 2.2, -1.75
    L = 11.0                    # screen length from the red ball's start to P (stands for 10^7)
    hop_height = 0.8            # height of the balls' small jumps

    def long_pause(self, seconds=3):
        # pauses left for the spoken commentary
        self.wait(seconds)

    def neper_setup(self, transformed=True, show_time=True):
        """Axes, P, stars, balls and time box. The balls follow self.blue_value() (position
        on the top axis) and self.red_dist() (screen distance from the red ball to P); while
        self.hop goes from 0 to 1, both balls jump over their axis instead of rolling."""
        r, x0, top_y, bot_y, L = self.r, self.x0, self.top_y, self.bot_y, self.L
        self.start_x, self.p_x = x0 + 1, x0 + 12

        self.t = ValueTracker(0)
        self.hop = ValueTracker(0)
        self.blue_value = lambda: self.t.get_value()
        self.red_dist = lambda: L * np.exp(-self.t.get_value() / L)   # v = x / L on screen

        def make_axis(y):
            axis = NumberLine(x_range=[0, 12, 1], length=12, include_numbers=True, font_size=26, color=GREY_B)
            axis.shift(np.array([x0, y, 0]) - axis.n2p(0))
            dots = DashedLine(axis.n2p(12), RIGHT * config.frame_x_radius + UP * y,
                              dash_length=0.06, dashed_ratio=0.5, color=GREY_B)
            return axis, dots

        self.top_axis, self.top_dots = make_axis(top_y)
        self.top_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(self.top_axis.n2p(0))
        self.bot_star = Star(outer_radius=0.12, color=GREEN, fill_opacity=1).move_to(
            np.array([self.start_x, bot_y, 0]))
        self.p_dot = Dot(np.array([self.p_x if transformed else x0, bot_y, 0]), color=YELLOW, radius=0.08)
        self.p_label = MathTex("P", color=YELLOW).next_to(self.p_dot, UP, buff=0.2)
        if transformed:
            # Neper's segment: from the red ball's start to P
            self.bot_line = Line(np.array([self.start_x, bot_y, 0]), np.array([self.p_x, bot_y, 0]),
                                 color=GREY_B, stroke_width=2)
            bottom = [self.bot_line]
        else:
            self.bot_axis, self.bot_dots = make_axis(bot_y)
            bottom = [self.bot_axis, self.bot_dots]

        self.top_ball, top_spin = beach_ball(np.array([x0, top_y + r, 0]), r, (BLUE, YELLOW))
        self.bot_ball, bot_spin = beach_ball(np.array([self.start_x, bot_y + r, 0]), r, (RED, WHITE))
        self.top_ball.set_z_index(1)
        self.bot_ball.set_z_index(1)

        def lift():
            p = self.hop.get_value()
            return self.hop_height * 4 * p * (1 - p) if 0 < p < 1 else 0

        def follow(spin, get_x):
            state = {"x": get_x(), "lift": 0}

            def update(mob, dt):
                x, height = get_x(), lift()
                mob.shift(RIGHT * (x - state["x"]) + UP * (height - state["lift"]))
                if height == 0 and state["lift"] == 0:      # rolls on the axis, not in the air
                    spin.rotate(-(x - state["x"]) / r, about_point=spin.get_center())
                state["x"], state["lift"] = x, height
            return update

        self.top_ball.add_updater(follow(top_spin, lambda: x0 + self.blue_value()))
        self.bot_ball.add_updater(follow(bot_spin, lambda: self.p_x - self.red_dist()))

        self.add(self.top_axis, self.top_dots, self.top_star, *bottom, self.p_dot, self.p_label,
                 self.bot_star, self.top_ball, self.bot_ball)

        if show_time:
            self.time_display = VGroup(MathTex("t =", font_size=40), DecimalNumber(0, num_decimal_places=2,
                                                                                    font_size=40))
            widest = VGroup(MathTex("t =", font_size=40), DecimalNumber(10, font_size=40)).arrange(RIGHT, buff=0.2)
            self.time_box = SurroundingRectangle(widest, color=WHITE, buff=0.15, corner_radius=0.1)
            self.time_box.to_corner(UL, buff=0.25)

            def update_time(m):
                m[1].set_value(self.t.get_value())
                m.arrange(RIGHT, buff=0.2).move_to(self.time_box)
            self.time_display.add_updater(update_time)
            self.time_display.update()
            self.add(self.time_box, self.time_display)

    # ---- helpers shared by several scenes ----
    def red_ball_x(self):
        return self.p_x - self.red_dist()

    def distance_arrow(self):
        """Red double arrow from the red ball to P, under the axis, with its name below."""
        y = self.bot_y - 0.45

        def build():
            start = np.array([self.red_ball_x(), y, 0])
            end = np.array([self.p_x, y, 0])
            return DoubleArrow(start, end, buff=0, color=RED, stroke_width=4, tip_length=0.18,
                               max_tip_length_to_length_ratio=0.2)

        arrow = build()
        arrow.add_updater(lambda m: m.become(build()))
        return arrow

    def roll_to(self, t_target, seconds_per_unit=1.4, rate_func=linear):
        self.play(self.t.animate.set_value(t_target),
                  run_time=abs(t_target - self.t.get_value()) * seconds_per_unit, rate_func=rate_func)

    def live_values(self, font_size=40):
        """y = ...   x = ... with the true values: y = t, x = 10^7 e^(-t / 10^7)."""
        row = VGroup(VGroup(MathTex("y =", color=BLUE, font_size=font_size),
                            DecimalNumber(0, num_decimal_places=2, color=BLUE, font_size=font_size)),
                     VGroup(MathTex("x =", color=RED, font_size=font_size),
                            DecimalNumber(NEPER_X0, num_decimal_places=2, color=RED, font_size=font_size)))

        def update(m):
            s = self.t.get_value()
            m[0][1].set_value(s)
            m[1][1].set_value(NEPER_X0 * np.exp(-s / NEPER_X0))
            m[0].arrange(RIGHT, buff=0.15)
            m[1].arrange(RIGHT, buff=0.15)
            m.arrange(RIGHT, buff=0.9)
        row.update_values = update
        update(row)
        return row


def colored_math(*parts, font_size=40):
    """MathTex built from (tex, color) pairs, each part in its own color."""
    tex = MathTex(*[p for p, _ in parts], font_size=font_size)
    for sub, (_, color) in zip(tex, parts):
        sub.set_color(color)
    return tex


NAPLOG = r"\text{Nap.Log}"


class NeperContinu(NeperMixin, MovingCameraScene):
    def construct(self):
        self.neper_setup(transformed=False)
        self.long_pause(2)

        # ---- From the usual axes to Neper's segment ----
        # P slides to the end of the solid line
        self.play(VGroup(self.p_dot, self.p_label).animate.shift(RIGHT * 12), run_time=2.5, rate_func=smooth)
        # graduations, numbers and dotted end go; the part from 0 to 1 fades out
        segment = Line(np.array([self.start_x, self.bot_y, 0]), np.array([self.x0 + 12, self.bot_y, 0]),
                       color=GREY_B, stroke_width=2)
        self.play(LaggedStart(*[FadeOut(n, shift=DOWN * 0.3) for n in self.bot_axis.numbers], lag_ratio=0.05),
                  FadeOut(self.bot_axis.ticks), FadeOut(self.bot_dots), run_time=1.5)
        self.add(segment)
        self.bring_to_front(self.p_dot, self.p_label, self.bot_star, self.bot_ball)
        self.play(FadeOut(self.bot_axis), run_time=1.2)
        self.p_x = self.x0 + 12

        # the distance from the red ball to P: x = 10^7 at the start
        arrow = self.distance_arrow()
        name = MathTex("x = 10^{7}", color=RED, font_size=40)
        name_box = SurroundingRectangle(name, color=RED, buff=0.12, corner_radius=0.08)
        name_group = VGroup(name, name_box)
        name_group.add_updater(lambda m: m.next_to(arrow, DOWN, buff=0.15))
        name_group.update()
        self.play(GrowFromCenter(arrow), run_time=1.5)
        self.play(FadeIn(name_group, shift=UP * 0.2))
        self.long_pause()

        # ---- Central box: y and x (distance to P) with their true values ----
        values = self.live_values()
        widest = self.live_values()
        widest[0][1].set_value(12)
        widest.update_values = None
        widest[0].arrange(RIGHT, buff=0.15)
        widest.arrange(RIGHT, buff=0.9)
        box_center = UP * 0.25
        box = SurroundingRectangle(widest.move_to(box_center), color=WHITE, buff=0.25, corner_radius=0.1)
        values.move_to(box_center)
        values.add_updater(lambda m: (m.update_values(m), m.move_to(box_center)))
        self.play(Create(box), FadeIn(values))
        self.long_pause()

        # the name under the arrow now just says "x": it changes as the ball moves
        x_name = MathTex("x", color=RED, font_size=40)
        x_box = SurroundingRectangle(x_name, color=RED, buff=0.12, corner_radius=0.08)
        new_name = VGroup(x_name, x_box).next_to(arrow, DOWN, buff=0.15)
        name_group.clear_updaters()
        self.play(ReplacementTransform(name_group, new_name))
        new_name.add_updater(lambda m: m.next_to(arrow, DOWN, buff=0.15))

        # ---- First back and forth: the red ball slows down as it gets closer to P ----
        self.roll_to(7)
        self.long_pause(2)
        self.roll_to(0, seconds_per_unit=0.6, rate_func=smooth)
        self.long_pause(2)

        # ---- y = Nap.Log(x) appears, second back and forth ----
        law = colored_math(("y", BLUE), ("=", WHITE), (NAPLOG + "(", WHITE), ("x", RED), (")", WHITE),
                           font_size=44)
        layout = VGroup(law.copy(), widest.copy()).arrange(DOWN, buff=0.25).move_to(box_center)
        law.move_to(layout[0])
        values_center = layout[1].get_center()
        values.clear_updaters()
        values.add_updater(lambda m: (m.update_values(m), m.move_to(values_center)))
        self.play(Transform(box, SurroundingRectangle(layout, color=WHITE, buff=0.25, corner_radius=0.1)),
                  values.animate.move_to(values_center), run_time=1)
        self.play(Write(law), run_time=1.5)
        self.play(Circumscribe(law, color=YELLOW))
        self.long_pause()
        self.roll_to(7)
        self.long_pause(2)
        self.roll_to(0, seconds_per_unit=0.6, rate_func=smooth)
        self.long_pause(2)

        # ---- The product rule: the naive guess, then the corrected rule ----
        A, D = PURPLE, RED

        def product_rule(scaled):
            left = [(NAPLOG + "(", WHITE), ("A", A), (r"\times", WHITE), ("D", D)]
            if scaled:
                left.append((r"/\,10^{7}", YELLOW))
            return colored_math(*left, (")", WHITE), ("=", WHITE), (NAPLOG + "(", WHITE), ("A", A), (")", WHITE),
                                ("+", WHITE), (NAPLOG + "(", WHITE), ("D", D), (")", WHITE), font_size=40)

        guess = product_rule(False)
        question = MathTex("?", color=YELLOW, font_size=56)
        guess_row = VGroup(guess, question).arrange(RIGHT, buff=0.3)
        rule = product_rule(True)
        rule_layout = VGroup(law.copy(), rule.copy()).arrange(DOWN, buff=0.3).move_to(box_center)
        guess_row.move_to(rule_layout[1])
        rule.move_to(rule_layout[1])
        self.play(FadeOut(values), Transform(box, SurroundingRectangle(rule_layout, color=WHITE, buff=0.25,
                                                                       corner_radius=0.1)),
                  law.animate.move_to(rule_layout[0]))
        self.play(Write(guess), run_time=2)
        self.play(FadeIn(question, scale=1.5))
        self.play(Wiggle(question))
        self.long_pause(4)
        # the correction: 10^7 plays the part of 1
        self.play(FadeOut(question), TransformMatchingTex(guess, rule), run_time=2)
        self.play(Circumscribe(rule[4], color=YELLOW), Indicate(rule[4], color=YELLOW))
        self.long_pause(5)

        # the rule goes, the values come back
        self.play(FadeOut(rule), law.animate.move_to(layout[0]),
                  Transform(box, SurroundingRectangle(layout, color=WHITE, buff=0.25, corner_radius=0.1)))
        self.play(FadeIn(values))
        self.long_pause(3)


class NeperSauts(NeperMixin, MovingCameraScene):
    q_screen = 1 - 1 / NeperMixin.L     # on screen, the first jump of the red ball is 1 unit, like the blue one

    def construct(self):
        self.neper_setup(transformed=True)
        L = self.L
        blue, red_d = ValueTracker(0), ValueTracker(L)
        self.blue_value = blue.get_value
        self.red_dist = red_d.get_value
        self.time_display[1].num_decimal_places = 0
        self.time_display.update()

        box_center = UP * 0.25
        marks = VGroup()

        def mark(n):
            # small ticks with Y_n and X_n at the balls' current positions
            top_p = np.array([self.x0 + blue.get_value(), self.top_y, 0])
            bot_p = np.array([self.red_ball_x(), self.bot_y, 0])
            group = VGroup(
                Line(top_p + DOWN * 0.15, top_p + UP * 0.15, color=BLUE, stroke_width=4),
                MathTex(f"Y_{{{n}}}", color=BLUE, font_size=30).next_to(top_p, DOWN, buff=0.55),
                Line(bot_p + DOWN * 0.15, bot_p + UP * 0.15, color=RED, stroke_width=4),
                MathTex(f"X_{{{n}}}", color=RED, font_size=30).next_to(bot_p, DOWN, buff=0.25),
            )
            return group

        def jump(n, run_time=1.4):
            # both balls jump: one unit of time later, Y_n = n Y_1 and X_n = X_0 q^n
            self.hop.set_value(0)
            self.play(blue.animate.set_value(n), red_d.animate.set_value(L * self.q_screen ** n),
                      self.hop.animate.set_value(1), self.t.animate.set_value(n), run_time=run_time,
                      rate_func=smooth)
            self.hop.set_value(0)

        def box_row(*cells):
            row = VGroup(*cells).arrange(RIGHT, buff=1.0)
            return row

        # Step 0
        first = mark(0)
        marks.add(first)
        row_a = box_row(colored_math(("Y_0", BLUE), ("= 0", BLUE)),
                        colored_math(("X_0", RED), ("= 10^{7}", RED)))
        widest = VGroup(box_row(colored_math((r"Y_1 \approx 1.00000005", BLUE)),
                                colored_math((r"X_1 = 10^{7} - 1 = 9{,}999{,}999", RED))),
                        box_row(colored_math((r"Y_5 = 5\,Y_1", BLUE)), colored_math((r"X_5 = X_0\,q^{5}", RED))),
                        ).arrange(DOWN, buff=0.3).move_to(box_center)
        box = SurroundingRectangle(widest, color=WHITE, buff=0.25, corner_radius=0.1)
        row_a.move_to(widest[0])
        self.play(FadeIn(first))
        self.play(Create(box), FadeIn(row_a))
        self.long_pause()

        # Step 1: the red ball has run exactly 1 unit, X_1 = 10^7 - 1; Y_1 is just over 1
        jump(1)
        marks.add(mark(1))
        row_1 = box_row(colored_math((r"Y_1 \approx 1.00000005", BLUE)),
                        colored_math((r"X_1 = 10^{7} - 1 = 9{,}999{,}999", RED))).move_to(widest[0])
        self.play(FadeIn(marks[-1]), ReplacementTransform(row_a, row_1), run_time=1.5)
        self.play(Indicate(row_1[0], color=YELLOW))
        self.long_pause(5)

        # Steps 2 to 5: only the names X_n, and Y_n = n Y_1
        row_b = None
        for n in range(2, 6):
            jump(n)
            marks.add(mark(n))
            new_b = box_row(colored_math((rf"Y_{n} = {n}\,Y_1", BLUE)), colored_math((rf"X_{n}", RED)))
            new_b.move_to(widest[1])
            self.play(FadeIn(marks[-1]), FadeIn(new_b) if row_b is None else ReplacementTransform(row_b, new_b))
            row_b = new_b
            self.long_pause(2)
        self.long_pause(2)

        # ---- Again, with the ratio q: X_1 = X_0 q, so X_n = X_0 q^n ----
        self.hop.set_value(0)
        self.play(blue.animate.set_value(0), red_d.animate.set_value(L), self.hop.animate.set_value(1),
                  self.t.animate.set_value(0), FadeOut(row_b), run_time=2, rate_func=smooth)
        self.hop.set_value(0)
        row_q = box_row(colored_math((r"Y_1 \approx 1.00000005", BLUE)),
                        colored_math((r"X_1 = X_0\,q", RED), (r",\quad q = 1 - 10^{-7}", WHITE)))
        row_q.move_to(widest[0])
        new_box = SurroundingRectangle(VGroup(widest.copy(), row_q.copy()), color=WHITE, buff=0.25, corner_radius=0.1)
        self.play(ReplacementTransform(row_1, row_q), Transform(box, new_box), run_time=1.5)
        self.play(Circumscribe(row_q[1], color=YELLOW))
        self.long_pause(4)

        row_b = None
        for n in range(1, 6):
            jump(n)
            new_b = box_row(colored_math((rf"Y_{n} = {n}\,Y_1" if n > 1 else r"Y_1", BLUE)),
                            colored_math((rf"X_{n} = X_0\,q^{{{n}}}" if n > 1 else r"X_1 = X_0\,q", RED)))
            new_b.move_to(widest[1])
            self.play(FadeIn(new_b) if row_b is None else ReplacementTransform(row_b, new_b))
            row_b = new_b
            self.long_pause(2)
        self.play(Indicate(row_b[0], color=YELLOW), Indicate(row_b[1], color=YELLOW))
        self.long_pause(4)


class NeperTable(NeperMixin, MovingCameraScene):
    q_screen = NeperSauts.q_screen

    def construct(self):
        self.neper_setup(transformed=True, show_time=False)
        L = self.L
        blue, red_d = ValueTracker(0), ValueTracker(L)
        self.blue_value = blue.get_value
        self.red_dist = red_d.get_value
        self.long_pause(1)

        # Zoom out: the figure goes to the left half, the table is drawn on the right
        edge = config.frame_x_radius
        self.play(self.camera.frame.animate.scale(2).move_to(RIGHT * edge), run_time=2.5, rate_func=smooth)

        fs = 60                                    # font size in the zoomed-out view (looks like 30)
        cols = [9.4, 13.5, 18.8]                   # x of the columns: step, X, Y
        top, row_h = 5.6, 1.35

        def cell(tex, color, col, row):
            return MathTex(tex, color=color, font_size=fs).move_to(np.array([cols[col], top - row * row_h, 0]))

        header = VGroup(Tex(r"\'Etape", font_size=fs).move_to(np.array([cols[0], top + 1.5, 0])),
                        MathTex("X", color=RED, font_size=fs).move_to(np.array([cols[1], top + 1.5, 0])),
                        MathTex(r"Y = " + NAPLOG + "(X)", color=BLUE, font_size=fs).move_to(
                            np.array([cols[2], top + 1.5, 0])))
        rule = Line(np.array([8.4, top + 0.75, 0]), np.array([21.0, top + 0.75, 0]), color=GREY_B, stroke_width=3)
        self.play(Write(header), Create(rule), run_time=2)

        symbolic = [
            ("0", r"X_0 = 10^{7}", r"Y_0 = 0"),
            ("1", r"X_0\,q", r"Y_1"),
            ("2", r"X_0\,q^{2}", r"2\,Y_1"),
            ("3", r"X_0\,q^{3}", r"3\,Y_1"),
            ("4", r"X_0\,q^{4}", r"4\,Y_1"),
        ]
        rows = VGroup()

        def jump(n):
            self.hop.set_value(0)
            self.play(blue.animate.set_value(n), red_d.animate.set_value(L * self.q_screen ** n),
                      self.hop.animate.set_value(1), run_time=1.3, rate_func=smooth)
            self.hop.set_value(0)

        for n, (step, x_tex, y_tex) in enumerate(symbolic):
            if n > 0:
                jump(n)
            row = VGroup(cell(step, WHITE, 0, n), cell(x_tex, RED, 1, n), cell(y_tex, BLUE, 2, n))
            self.play(FadeIn(row, shift=LEFT * 0.3))
            rows.add(row)
            self.long_pause(1.5)
        dots = VGroup(*[cell(r"\vdots", c, i, 5) for i, c in enumerate([WHITE, RED, BLUE])])
        general = VGroup(cell("n", WHITE, 0, 6), cell(r"X_0\,q^{n}", RED, 1, 6), cell(r"n\,Y_1", BLUE, 2, 6))
        self.play(FadeIn(dots), FadeIn(general, shift=LEFT * 0.3))
        self.play(Circumscribe(general, color=YELLOW))
        self.long_pause(4)

        # ---- The letters become numbers: what Neper had to compute by hand ----
        numeric = [
            ("0", r"10{,}000{,}000", r"0"),
            ("1", r"9{,}999{,}999", r"1.00000005"),
            ("2", r"9{,}999{,}998.0000001", r"2.0000001"),
            ("3", r"9{,}999{,}997.0000003", r"3.00000015"),
            ("4", r"9{,}999{,}996.0000006", r"4.0000002"),
        ]
        for n, (step, x_tex, y_tex) in enumerate(numeric):
            self.play(ReplacementTransform(rows[n][1], cell(x_tex, RED, 1, n)),
                      ReplacementTransform(rows[n][2], cell(y_tex, BLUE, 2, n)), run_time=0.8)
        self.long_pause(3)

        # ---- The numbers scroll by: hundreds of lines to compute ----
        # a fixed set of rows whose values follow N; they slide up as N grows
        n_rows = 8
        N = ValueTracker(0)
        window_top, window_bottom = top + 0.4, top - (n_rows - 1) * row_h - 0.4

        def number(decimals, color, commas=True):
            return DecimalNumber(0, num_decimal_places=decimals, color=color, font_size=fs,
                                 group_with_commas=commas)

        slots = VGroup(*[VGroup(Integer(0, font_size=fs), number(7, RED), number(8, BLUE, commas=False))
                         for _ in range(n_rows)])

        def scroll(group):
            value = N.get_value()
            first, frac = int(np.floor(value)), value - np.floor(value)
            for i, slot in enumerate(group):
                n = first + i
                y = top - (i - frac) * row_h
                slot[0].set_value(n)
                slot[1].set_value(NEPER_X0 * NEPER_Q ** n)
                slot[2].set_value(n * NEPER_Y1)
                for c, m in enumerate(slot):
                    m.move_to(np.array([cols[c], y, 0]))
                # fade out at the top and at the bottom of the window
                fade = min(1, max(0, (window_top - y) / 0.6), max(0, (y - window_bottom) / 0.6))
                slot.set_opacity(fade)

        scroll(slots)
        self.play(FadeOut(rows), FadeOut(dots), FadeOut(general), FadeIn(slots), run_time=1)
        slots.add_updater(scroll)
        self.play(N.animate.set_value(12), run_time=4, rate_func=linear)
        self.play(N.animate.set_value(1000), run_time=8, rate_func=rate_functions.ease_in_quad)
        slots.clear_updaters()
        self.long_pause(4)


class NeperEtLn(NeperMixin, MovingCameraScene):
    def construct(self):
        self.neper_setup(transformed=True)
        arrow = self.distance_arrow()
        x_name = MathTex("x", color=RED, font_size=40)
        name = VGroup(x_name, SurroundingRectangle(x_name, color=RED, buff=0.12, corner_radius=0.08))
        name.add_updater(lambda m: m.next_to(arrow, DOWN, buff=0.15))
        name.update()
        self.add(arrow, name)

        # y = Nap.Log(x) = -10^7 ln(x / 10^7), with the live values underneath
        box_center = UP * 0.25
        formula = colored_math(("y", BLUE), ("=", WHITE), (NAPLOG + "(", WHITE), ("x", RED), (")", WHITE),
                               ("=", WHITE), (r"-10^{7}\,\ln\!\Big(", WHITE), ("x", RED), (r"\,/\,10^{7}\Big)", WHITE),
                               font_size=44)
        values = self.live_values()
        widest = self.live_values()
        widest[0][1].set_value(12)
        widest.update_values = None
        widest[0].arrange(RIGHT, buff=0.15)
        widest.arrange(RIGHT, buff=0.9)
        layout = VGroup(formula.copy(), widest).arrange(DOWN, buff=0.3).move_to(box_center)
        formula.move_to(layout[0])
        values_center = layout[1].get_center()
        values.add_updater(lambda m: (m.update_values(m), m.move_to(values_center)))
        values.update()
        box = SurroundingRectangle(layout, color=WHITE, buff=0.25, corner_radius=0.1)
        self.long_pause(1.5)
        self.play(Create(box), FadeIn(values))
        self.long_pause(1)
        self.play(Write(formula[:5]), run_time=1.5)
        self.long_pause(2)
        self.play(Write(formula[5:]), run_time=2)
        self.play(Circumscribe(formula[5:], color=YELLOW))
        self.long_pause(4)

        self.roll_to(8)
        self.long_pause(3)
        self.roll_to(0, seconds_per_unit=0.6, rate_func=smooth)
        self.long_pause(4)
