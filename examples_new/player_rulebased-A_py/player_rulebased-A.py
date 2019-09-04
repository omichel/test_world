#!/usr/bin/env python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

import math
import numpy as np
import os
import sys

import helper

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../common')
try:
    from participant import Participant, Game, Frame
except ImportError as err:
    print('player_rulebased-A: \'participant\' module cannot be imported:', err)
    raise


# shortcuts
X = Frame.X
Y = Frame.Y
TH = Frame.TH
ACTIVE = Frame.ACTIVE
TOUCH = Frame.TOUCH

class RuleBasedA(Participant):
    def init(self, info):
        self.game_time = info['game_time']
        self.number_of_robots = info['number_of_robots']
        self.field = info['field']
        self.goal = info['goal']
        self.penalty_area = info['penalty_area']
        self.resolution = info['resolution']
        self.ball_radius = info['ball_radius']
        self.robot_size = info['robot_size']
        self.max_linear_velocity = info['max_linear_velocity']
        self.colorChannels = 3
        self.cur_posture = []
        self.cur_ball = []
        self.prev_posture = []
        self.prev_ball = []
        self.previous_frame = Frame()
        self.cur_count = 0
        self.end_count = 0
        self.prev_sender = None
        self.sender = None
        self.touch = [False,False,False,False,False]
        self.prev_receiver = None
        self.receiver = None
        self.def_idx = 0
        self.atk_idx = 0
        self.closest_order = []
        self.player_state = [None,None,None,None,None]
        self.wheels = [0 for _ in range(10)]

    def update(self, frame):
        if frame.end_of_frame:
            if frame.reset_reason != Game.NONE:
                self.previous_frame = frame
            self.get_coord(frame)
            self.find_closest_robot()

            if frame.reset_reason == Game.EPISODE_END:
                # EPISODE_END is sent instead of GAME_END when 'repeat' option is set to 'true'
                # to mark the end of episode
                # you can reinitialize the parameters, count the number of episodes done, etc. here

                # this example does not do anything at episode end
                pass

            if frame.reset_reason == Game.HALFTIME:
                # halftime is met - from next frame, frame.half_passed will be set to True
                # although the simulation switches sides,
                # coordinates and images given to your AI soccer algorithm will stay the same
                # that your team is red and located on left side whether it is 1st half or 2nd half

                # this example does not do anything at halftime
                pass

            ##############################################################################
            if frame.game_state == Game.STATE_DEFAULT:
                # robot functions in STATE_DEFAULT
                # goalkeeper simply executes goalkeeper algorithm on its own
                self.goalkeeper(0)

                # defenders and forwards can pass ball to each other if necessary
                self.pass_play(frame, [1, 2, 3, 4])

                self.set_speeds(self.wheels)
            ##############################################################################
            elif frame.game_state == Game.STATE_KICKOFF:
                #  if the ball belongs to my team, initiate kickoff
                if (frame.ball_ownership):
                    self.set_target_position(4, 0, 0, 1.4, 3.0, 0.4, False)

                self.set_speeds(self.wheels)
            ##############################################################################
            elif frame.game_state == Game.STATE_GOALKICK:
                # if the ball belongs to my team,
                # drive the goalkeeper to kick the ball
                if (frame.ball_ownership):
                    self.set_wheel_velocity(0, self.max_linear_velocity[0], self.max_linear_velocity[0], True)

                self.set_speeds(self.wheels)
            ##############################################################################
            elif frame.game_state == Game.STATE_CORNERKICK:
                # just play as simple as possible
                self.goalkeeper(0)
                self.defender(1)
                self.defender(2)
                self.forward(3)
                self.forward(4)
                self.set_speeds(self.wheels)
            ##############################################################################
            elif frame.game_state == Game.STATE_PENALTYKICK:
                # if the ball belongs to my team,
                # drive the forward to kick the ball
                if frame.ball_ownership:
                    self.set_wheel_velocity(4, self.max_linear_velocity[0], self.max_linear_velocity[0], True)
                self.set_speeds(self.wheels)
            ##############################################################################

        self.previous_frame = frame

    # a basic goalkeeper rulebased algorithm
    def goalkeeper(self, id):
        # default desired position
        x = -self.field[X] / 2 + self.robot_size[id] / 2 + 0.05
        y = max(min(self.cur_ball[Y], (self.goal[Y] / 2 - self.robot_size[id] / 2)),
                -self.goal[Y] / 2 + self.robot_size[id] / 2)

        # if the robot is inside the goal, try to get out
        if (self.cur_posture[id][X] < -self.field[X] / 2):
            if (self.cur_posture[id][Y] < 0):
                self.set_target_position(id, x, self.cur_posture[id][Y] + 0.2, 1.4, 5.0, 0.4, False)
            else:
                self.set_target_position(id, x, self.cur_posture[id][Y] - 0.2, 1.4, 5.0, 0.4, False)
        # if the goalkeeper is outside the penalty area
        elif (not self.in_penalty_area(self.cur_posture[id], Frame.MY_TEAM)):
            # return to the desired position
            self.set_target_position(id, x, y, 1.4, 5.0, 0.4, True)
        # if the goalkeeper is inside the penalty area
        else:
            # if the ball is inside the penalty area
            if (self.in_penalty_area(self.cur_ball, Frame.MY_TEAM)):
                # if the ball is behind the goalkeeper
                if (self.cur_ball[X] < self.cur_posture[id][X]):
                    # if the ball is not blocking the goalkeeper's path
                    if (abs(self.cur_ball[Y] - self.cur_posture[id][Y]) > 2 * self.robot_size[id]):
                        # try to get ahead of the ball
                        self.set_target_position(id, self.cur_ball[X] - self.robot_size[id], self.cur_posture[id][Y],
                                                 1.4, 5.0, 0.4, False)
                    else:
                        # just give up and try not to make a suicidal goal
                        self.angle(id, math.pi / 2)
                # if the ball is ahead of the goalkeeper
                else:
                    desired_th = self.direction_angle(id, self.cur_ball[X], self.cur_ball[Y])
                    rad_diff = helper.trim_radian(desired_th - self.cur_posture[id][TH])
                    # if the robot direction is too away from the ball direction
                    if (rad_diff > math.pi / 3):
                        # give up kicking the ball and block the goalpost
                        self.set_target_position(id, x, y, 1.4, 5.0, 0.4, False)
                    else:
                        # try to kick the ball away from the goal
                        self.set_target_position(id, self.cur_ball[X], self.cur_ball[Y], 1.4, 3.0, 0.8, True)
            # if the ball is not in the penalty area
            else:
                # if the ball is within alert range and y position is not too different
                if self.cur_ball[X] < -self.field[X] / 2 + 1.5 * self.penalty_area[X] and \
                   abs(self.cur_ball[Y]) < 1.5 * self.penalty_area[Y] / 2 and \
                   abs(self.cur_ball[Y] - self.cur_posture[id][Y]) < 0.2:
                    self.face_specific_position(id, self.cur_ball[X], self.cur_ball[Y])
                # otherwise
                else:
                    self.set_target_position(id, x, y, 1.4, 5.0, 0.4, True)

    # a basic defender rulebased algorithm
    def defender(self, id):
        # if the robot is inside the goal, try to get out
        if (self.cur_posture[id][X] < -self.field[X] / 2):
            if (self.cur_posture[id][Y] < 0):
                self.set_target_position(id, -0.7 * self.field[X] / 2, self.cur_posture[id][Y] + 0.2, 1.4, 3.5, 0.6, False)
            else:
                self.set_target_position(id, -0.7 * self.field[X] / 2, self.cur_posture[id][Y] - 0.2, 1.4, 3.5, 0.6, False)
            return
        # the defender may try to shoot if condition meets
        if (id == self.def_idx and self.shoot_chance(id) and self.cur_ball[X] < 0.3 * self.field[X] / 2):
            self.set_target_position(id, self.cur_ball[X], self.cur_ball[Y], 1.4, 5.0, 0.4, True)
            return

        # if this defender is closer to the ball than the other defender
        if (id == self.def_idx):
            # ball is on our side
            if (self.cur_ball[X] < 0):
                # if the robot can push the ball toward opponent's side, do it
                if (self.cur_posture[id][X] < self.cur_ball[X] - self.ball_radius):
                    self.set_target_position(id, self.cur_ball[X], self.cur_ball[Y], 1.4, 5.0, 0.4, True)
                else:
                    # otherwise go behind the ball
                    if (abs(self.cur_ball[Y] - self.cur_posture[id][Y]) > 0.3):
                        self.set_target_position(id,
                                                 max(self.cur_ball[X] - 0.5, -self.field[X] / 2 + self.robot_size[id] / 2),
                                                 self.cur_ball[Y], 1.4, 3.5, 0.6, False)
                    else:
                        self.set_target_position(id,
                                                 max(self.cur_ball[X] - 0.5, -self.field[X] / 2 + self.robot_size[id] / 2),
                                                 self.cur_posture[id][Y], 1.4, 3.5, 0.6, False)
            else:
                self.set_target_position(id, -0.7 * self.field[X] / 2, self.cur_ball[Y], 1.4, 3.5, 0.4, False)
        # if this defender is not closer to the ball than the other defender
        else:
            # ball is on our side
            if (self.cur_ball[X] < 0):
                # ball is on our left
                if (self.cur_ball[Y] > self.goal[Y] / 2 + 0.15):
                    self.set_target_position(id,
                                             max(self.cur_ball[X] - 0.5, -self.field[X] / 2 + self.robot_size[id] / 2 + 0.1),
                                             self.goal[Y] / 2 + 0.15, 1.4, 3.5, 0.4, False)
                # ball is on our right
                elif (self.cur_ball[Y] < -self.goal[Y] / 2 - 0.15):
                    self.set_target_position(id,
                                             max(self.cur_ball[X] - 0.5, -self.field[X] / 2 + self.robot_size[id] / 2 + 0.1),
                                             -self.goal[Y] / 2 - 0.15, 1.4, 3.5, 0.4, False)
                # ball is in center
                else:
                    self.set_target_position(id,
                                             max(self.cur_ball[X] - 0.5, -self.field[X] / 2 + self.robot_size[id] / 2 + 0.1),
                                             self.cur_ball[Y], 1.4, 3.5, 0.4, False)
            else:
                # ball is on right side
                if (self.cur_ball[Y] < 0):
                    self.set_target_position(id, -0.7 * self.field[X] / 2,
                                             min(self.cur_ball[Y] + 0.5, self.field[Y] / 2 - self.robot_size[id] / 2),
                                             1.4, 3.5, 0.4, False)
                # ball is on left side
                else:
                    self.set_target_position(id, -0.7 * self.field[X] / 2,
                                             max(self.cur_ball[Y] - 0.5, -self.field[Y] / 2 + self.robot_size[id] / 2),
                                             1.4, 3.5, 0.4, False)

    # a basic forward rulebased algorithm
    def forward(self, id):
        # if the robot is blocking the ball's path toward opponent side
        if self.cur_ball[X] > -0.3 * self.field[X] / 2 and \
           self.cur_ball[X] < 0.3 * self.field[X] / 2 and \
           self.cur_posture[id][X] > self.cur_ball[X] + 0.1 and \
           abs(self.cur_posture[id][Y] - self.cur_ball[Y]) < 0.3:
            if self.cur_ball[Y] < 0:
                self.set_target_position(id, self.cur_posture[id][X] - 0.25, self.cur_ball[Y] + 0.75, 1.4, 3.0, 0.8, False)
            else:
                self.set_target_position(id, self.cur_posture[id][X] - 0.25, self.cur_ball[Y] - 0.75, 1.4, 3.0, 0.8, False)
            return

        # if the robot can shoot from current position
        if (id == self.atk_idx and self.shoot_chance(id)):
            pred_ball = self.predict_ball_location(2)
            self.set_target_position(id, pred_ball[X], pred_ball[Y], 1.4, 5.0, 0.4, True)
            return

        # if the ball is coming toward the robot, seek for shoot chance
        if (id == self.atk_idx and self.ball_coming_toward_robot(id)):
            dx = self.cur_ball[X] - self.prev_ball[X]
            dy = self.cur_ball[Y] - self.prev_ball[Y]
            pred_x = (self.cur_posture[id][Y] - self.cur_ball[Y]) * dx / dy + self.cur_ball[X]
            steps = (self.cur_posture[id][Y] - self.cur_ball[Y]) / dy

            # if the ball will be located in front of the robot
            if (pred_x > self.cur_posture[id][X]):
                pred_dist = pred_x - self.cur_posture[id][X]
                # if the predicted ball location is close enough
                if (pred_dist > 0.1 and pred_dist < 0.3 and steps < 10):
                    # find the direction towards the opponent goal and look toward it
                    goal_angle = self.direction_angle(id, self.field[X] / 2, 0)
                    self.angle(id, goal_angle)
                    return

        # if this forward is closer to the ball than the other forward
        if (id == self.atk_idx):
            if (self.cur_ball[X] > -0.3 * self.field[X] / 2):
                # if the robot can push the ball toward opponent's side, do it
                if (self.cur_posture[id][X] < self.cur_ball[X] - self.ball_radius):
                    self.set_target_position(id, self.cur_ball[X], self.cur_ball[Y], 1.4, 5.0, 0.4, True)
                else:
                    # otherwise go behind the ball
                    if (abs(self.cur_ball[Y] - self.cur_posture[id][Y]) > 0.3):
                        self.set_target_position(id, self.cur_ball[X] - 0.2, self.cur_ball[Y], 1.4, 3.5, 0.6, False)
                    else:
                        self.set_target_position(id, self.cur_ball[X] - 0.2, self.cur_posture[id][Y], 1.4, 3.5, 0.6, False)
            else:
                self.set_target_position(id, -0.1 * self.field[X] / 2, self.cur_ball[Y], 1.4, 3.5, 0.4, False)
        # if this forward is not closer to the ball than the other forward
        else:
            if (self.cur_ball[X] > -0.3 * self.field[X] / 2):
                # ball is on our right
                if (self.cur_ball[Y] < 0):
                    self.set_target_position(id, self.cur_ball[X] - 0.25, self.goal[Y] / 2, 1.4, 3.5, 0.4, False)
                # ball is on our left
                else:
                    self.set_target_position(id, self.cur_ball[X] - 0.25, -self.goal[Y] / 2, 1.4, 3.5, 0.4, False)
            else:
                # ball is on right side
                if (self.cur_ball[Y] < 0):
                    self.set_target_position(id, -0.1 * self.field[X] / 2,
                                             min(-self.cur_ball[Y] - 0.5, self.field[Y] / 2 - self.robot_size[id] / 2),
                                             1.4, 3.5, 0.4, False)
                # ball is on left side
                else:
                    self.set_target_position(id, -0.1 * self.field[X] / 2,
                                             max(-self.cur_ball[Y] + 0.5, -self.field[Y] / 2 + self.robot_size[id] / 2),
                                             1.4, 3.5, 0.4, False)

    # set the left and right wheel velocities of robot with id 'id'
    # 'max_velocity' scales the velocities up to the point where at least one of wheel is operating at max velocity
    def set_wheel_velocity(self, id, left_wheel, right_wheel, max_velocity):
        multiplier = 1
        # wheel velocities need to be scaled so that none of wheels exceed the maximum velocity available
        # otherwise, the velocity above the limit will be set to the max velocity by the simulation program
        # if that happens, the velocity ratio between left and right wheels will be changed that the robot may not execute
        # turning actions correctly.
        if (abs(left_wheel) > self.max_linear_velocity[id] or abs(right_wheel) > self.max_linear_velocity[id] or max_velocity):
            if (abs(left_wheel) > abs(right_wheel)):
                multiplier = self.max_linear_velocity[id] / abs(left_wheel)
            else:
                multiplier = self.max_linear_velocity[id] / abs(right_wheel)

        self.wheels[2 * id] = left_wheel * multiplier
        self.wheels[2 * id + 1] = right_wheel * multiplier

    # let the robot with id 'id' move to a target position (x, y)
    # the trajectory to reach the target position is determined by several different parameters
    def set_target_position(self, id, x, y, scale, mult_lin, mult_ang, max_velocity):
        damping = 0.35
        ka = 0
        sign = 1
        # calculate how far the target position is from the robot
        dx = x - self.cur_posture[id][X]
        dy = y - self.cur_posture[id][Y]
        d_e = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        # calculate how much the direction is off
        desired_th = (math.pi / 2) if (dx == 0 and dy == 0) else math.atan2(dy, dx)
        d_th = desired_th - self.cur_posture[id][TH]
        while (d_th > math.pi):
            d_th -= 2 * math.pi
        while (d_th < -math.pi):
            d_th += 2 * math.pi

        # based on how far the target position is, set a parameter that
        # decides how much importance should be put into changing directions
        # farther the target is, less need to change directions fastly
        if (d_e > 1):
            ka = 17 / 90
        elif (d_e > 0.5):
            ka = 19 / 90
        elif (d_e > 0.3):
            ka = 21 / 90
        elif (d_e > 0.2):
            ka = 23 / 90
        else:
            ka = 25 / 90

        # if the target position is at rear of the robot, drive backward instead
        if (d_th > helper.d2r(95)):
            d_th -= math.pi
            sign = -1
        elif (d_th < helper.d2r(-95)):
            d_th += math.pi
            sign = -1

        # if the direction is off by more than 85 degrees,
        # make a turn first instead of start moving toward the target
        if (abs(d_th) > helper.d2r(85)):
            self.set_wheel_velocity(id, -mult_ang * d_th, mult_ang * d_th, False)
        # otherwise
        else:
            # scale the angular velocity further down if the direction is off by less than 40 degrees
            if (d_e < 5 and abs(d_th) < helper.d2r(40)):
                ka = 0.1
            ka *= 4

            # set the wheel velocity
            # 'sign' determines the direction [forward, backward]
            # 'scale' scales the overall velocity at which the robot is driving
            # 'mult_lin' scales the linear velocity at which the robot is driving
            # larger distance 'd_e' scales the base linear velocity higher
            # 'damping' slows the linear velocity down
            # 'mult_ang' and 'ka' scales the angular velocity at which the robot is driving
            # larger angular difference 'd_th' scales the base angular velocity higher
            # if 'max_velocity' is true, the overall velocity is scaled to the point
            # where at least one wheel is operating at maximum velocity
            self.set_wheel_velocity(id,
                                    sign * scale * (mult_lin * (
                                                1 / (1 + math.exp(-3 * d_e)) - damping) - mult_ang * ka * d_th),
                                    sign * scale * (mult_lin * (
                                                1 / (1 + math.exp(-3 * d_e)) - damping) + mult_ang * ka * d_th),
                                    max_velocity)

    # copy coordinates from frames to different variables just for convenience
    def get_coord(self, frame):
        self.cur_ball = frame.coordinates[Frame.BALL]
        self.cur_posture = frame.coordinates[Frame.MY_TEAM]
        self.cur_posture_op = frame.coordinates[Frame.OP_TEAM]
        self.prev_ball = self.previous_frame.coordinates[Frame.BALL]
        self.prev_posture = self.previous_frame.coordinates[Frame.MY_TEAM]
        self.prev_posture_op = self.previous_frame.coordinates[Frame.OP_TEAM]

    # find a defender and a forward closest to the ball
    def find_closest_robot(self):
        # find the closest defender
        min_idx = 0
        min_dist = 9999.99

        all_dist = []

        for i in [1, 2]:
            measured_dist = helper.dist(self.cur_ball[X], self.cur_posture[i][X],
                                        self.cur_ball[Y], self.cur_posture[i][Y])
            all_dist.append(measured_dist)
            if (measured_dist < min_dist):
                min_dist = measured_dist
                min_idx = i

        self.def_idx = min_idx

        # find the closest forward
        min_idx = 0
        min_dist = 9999.99

        for i in [3, 4]:
            measured_dist = helper.dist(self.cur_ball[X], self.cur_posture[i][X],
                                        self.cur_ball[Y], self.cur_posture[i][Y])
            all_dist.append(measured_dist)
            if (measured_dist < min_dist):
                min_dist = measured_dist
                min_idx = i

        self.atk_idx = min_idx

        # record the robot closer to the ball between the two too
        self.closest_order = np.argsort(all_dist) + 1

    # predict where the ball will be located after 'steps' steps
    def predict_ball_location(self, steps):
        dx = self.cur_ball[X] - self.prev_ball[X]
        dy = self.cur_ball[Y] - self.prev_ball[Y]
        return [self.cur_ball[X] + steps * dx, self.cur_ball[Y] + steps * dy]

    # let the robot face toward specific direction
    def face_specific_position(self, id, x, y):
        dx = x - self.cur_posture[id][X]
        dy = y - self.cur_posture[id][Y]

        desired_th = (math.pi / 2) if (dx == 0 and dy == 0) else math.atan2(dy, dx)

        self.angle(id, desired_th)

    # returns the angle toward a specific position from current robot posture
    def direction_angle(self, id, x, y):
        dx = x - self.cur_posture[id][X]
        dy = y - self.cur_posture[id][Y]

        return ((math.pi / 2) if (dx == 0 and dy == 0) else math.atan2(dy, dx))

    # turn to face 'desired_th' direction
    def angle(self, id, desired_th):
        mult_ang = 0.4

        d_th = desired_th - self.cur_posture[id][TH]
        d_th = helper.trim_radian(d_th)

        # the robot instead puts the direction rear if the angle difference is large
        if (d_th > helper.d2r(95)):
            d_th -= math.pi
        elif (d_th < helper.d2r(-95)):
            d_th += math.pi

        self.set_wheel_velocity(id, -mult_ang * d_th, mult_ang * d_th, False)

    # checks if a certain position is inside the penalty area of 'team'
    def in_penalty_area(self, obj, team):
        if (abs(obj[Y]) > self.penalty_area[Y] / 2):
            return False

        if (team == Frame.MY_TEAM):
            return (obj[X] < -self.field[X] / 2 + self.penalty_area[X])
        else:
            return (obj[X] > self.field[X] / 2 - self.penalty_area[X])

    # check if the ball is coming toward the robot
    def ball_coming_toward_robot(self, id):
        x_dir = abs(self.cur_posture[id][X] - self.prev_ball[X]) \
            > abs(self.cur_posture[id][X] - self.cur_ball[X])
        y_dir = abs(self.cur_posture[id][Y] - self.prev_ball[Y]) \
            > abs(self.cur_posture[id][Y] - self.cur_ball[Y])

        # ball is coming closer
        if (x_dir and y_dir):
            return True
        else:
            return False

    # check if the robot with id 'id' has a chance to shoot
    def shoot_chance(self, id):
        dx = self.cur_ball[X] - self.cur_posture[id][X]
        dy = self.cur_ball[Y] - self.cur_posture[id][Y]

        # if the ball is located further on left than the robot, it will be hard to shoot
        if (dx < 0):
            return False

        # if the robot->ball direction aligns with opponent's goal, the robot can shoot
        y = (self.field[X] / 2 - self.cur_ball[X]) * dy / dx + self.cur_posture[id][Y]
        if (abs(y) < self.goal[Y] / 2):
            return True
        else:
            return False

    # check if sender/receiver pair should be reset
    def reset_condition(self):
        # if the time is over, setting is reset
        if (self.end_count > 0 and self.end_count - self.cur_count < 0):
            return True

        # if there is no sender and receiver is not in shoot chance, setting is cleared
        if not self.sender is None:
            if not self.shoot_chance(self.sender):
                return True
        return False

    # check if a sender can be selected
    def set_sender_condition(self):
        for i in range(1,5):
            # if this robot is near the ball, it will be a sender candidate
            dist = helper.dist(self.cur_posture[i][X], self.cur_ball[X], self.cur_posture[i][Y], self.cur_ball[Y])
            if dist < 0.5 and self.cur_posture[i][ACTIVE]: return True
        return False

    # check if a receiver should be selected
    def set_receiver_condition(self):
        # if a sender exists, any other robots can be receiver candidates
        if self.sender != None and self.receiver == None: return True
        return False

    # select a sender
    def set_sender(self, _player_list):
        distance_list = []
        for sender in _player_list:
            predict_ball = self.predict_ball_location(3)
            ball_distance = helper.dist(predict_ball[X], self.cur_posture[sender][X], \
                predict_ball[Y], self.cur_posture[sender][Y])
            distance_list.append(ball_distance)

        # if the distance between ball and sender is less than 1, choose the closest robot as the sender
        if min(distance_list) < 1.0:
            return distance_list.index(min(distance_list)) + 1

        # otherwise, there is no sender
        return None

    # select a receiver
    def set_receiver(self, _player_list):
        receiver_op_dist_list = []
        for receiver in _player_list:
            temp_receiver_op_dist_list = []
            # the sender is not a receiver candidate
            if receiver == self.sender:
                receiver_op_dist_list.append(999)
                continue

            # the distance between the robot and opponents
            for op in range(1, 5): #[1,2,3,4]
                op_distance = helper.dist(self.cur_posture[receiver][X], self.cur_posture_op[op][X], \
                    self.cur_posture[receiver][Y], self.cur_posture_op[op][Y])
                temp_receiver_op_dist_list.append(op_distance)

            # save the shortest distance between this robot and one of opponents
            receiver_op_dist_list.append(min(temp_receiver_op_dist_list))

        receiver_ball_list = []
        for r in receiver_op_dist_list:
            # if the minimum distance between player and opponent's player is less than 0.5, this robot cannot be receiver
            if r < 0.5 or r == 999:
                receiver_ball_list.append(999)
                continue
            id = receiver_op_dist_list.index(r) + 1
            receiver_ball_distance = helper.dist(self.cur_ball[X], self.cur_posture[id][X], \
                self.cur_ball[Y], self.cur_posture[id][Y])
            receiver_ball_list.append(receiver_ball_distance)

        if min(receiver_ball_list) < 999:
            min_id = receiver_ball_list.index(min(receiver_ball_list)) + 1
            return min_id
        return None

    def pass_ball(self):
        if self.prev_sender == self.receiver or self.prev_receiver == self.sender:
            self.sender = self.prev_sender
            self.receiver = self.prev_receiver

        self.receive_ball()
        self.send_ball()

        self.prev_sender = self.sender
        self.prev_receiver = self.receiver

    def send_ball(self):
        if self.sender == None:
            return

        goal_dist = helper.dist(4.0, self.cur_posture[self.sender][X], 0, self.cur_posture[self.sender][Y])
        # if the sender has a shoot chance, it tries to shoot
        if self.shoot_chance(self.sender):
            if goal_dist > 0.3 * self.field[X] / 2:
                self.actions(self.sender, 'dribble', refine=True)
                return
            else:
                self.actions(self.sender, 'kick')
                return

        # if the receiver exists, get the distance between the sender and the receiver
        sender_receiver_dist = None
        if not self.receiver == None:
            sender_receiver_dist = helper.dist(self.cur_posture[self.sender][X], \
                self.cur_posture[self.receiver][X],self.cur_posture[self.sender][Y], self.cur_posture[self.receiver][Y])

        # if the sender is close to the receiver, the sender kicks the ball
        if not sender_receiver_dist == None:
            if sender_receiver_dist < 0.3 and not self.cur_posture[self.receiver][TOUCH]:
                self.actions(self.sender, 'kick')
                return

        ift, theta_diff = self.is_facing_target(self.sender, self.cur_ball[X], self.cur_ball[Y])
        if not ift:
            # after the sender kicks, it stops
            if theta_diff > math.pi * 3/4:
                self.actions(self.sender, None)
                return
            else:
                self.actions(self.sender, 'follow', refine=True)
                return

        # if the ball is in front of the sender and sender is moving backward
        if self.cur_posture[self.sender][X] < - 0.8 * self.field[X] / 2:
            if self.cur_posture[self.sender][X] - self.prev_posture[self.sender][X] < 0:
                self.actions(self.sender, 'backward')

        self.actions(self.sender, 'dribble', refine=True)
        return

    def receive_ball(self):
        # if receiver does not exist, do nothing
        if self.receiver == None:
            return

        goal_dist = helper.dist(4.0, self.cur_posture[self.receiver][X], 0, self.cur_posture[self.receiver][Y])
        # if sender is in shoot chance, receiver does nothing(reset)
        if not self.sender == None:
            if self.shoot_chance(self.sender):
                self.actions(self.receiver,None)
                return
        # if receiver is in shoot chance, receiver try to shoot
        if self.shoot_chance(self.receiver):
            if goal_dist > 0.3 * self.field[X] / 2:
                self.actions(self.receiver, 'dribble', refine=True)
                return
            else:
                self.actions(self.receiver, 'kick')
                return

        # if sender exists
        if not self.sender == None:
            s2risFace, _ = self.is_facing_target(self.sender, self.cur_posture[self.receiver][X], \
                self.cur_posture[self.receiver][Y],4)
            r2sisFace, _ = self.is_facing_target(self.receiver, self.cur_posture[self.sender][X], self.cur_posture[self.sender][Y],4)
            # if sender and receiver directs each other
            if s2risFace and r2sisFace:
                if self.cur_posture[self.receiver][TH] > 0 or self.cur_posture[self.receiver][TH] < -3:
                    self.actions(self.receiver,'follow', [self.prev_posture[self.receiver][X], \
                        self.prev_posture[self.receiver][Y] - 0.5 * self.field[Y]])
                    return
                self.actions(self.receiver, 'follow',[self.prev_posture[self.receiver][X], \
                    self.prev_posture[self.receiver][Y] + 0.5 * self.field[Y]])
                return

        r_point = self.cur_ball
        # if sender exists
        if not self.sender == None:
            r_point = self.receive_position()
        receiver_ball_dist = helper.dist(self.cur_ball[X], self.cur_posture[self.receiver][X], \
            self.cur_ball[Y],self.cur_posture[self.receiver][Y])
        # if ball is close to receiver
        if receiver_ball_dist > 0.3 * self.field[X] / 2:
            self.actions(self.receiver, 'follow', [r_point[X], r_point[Y]], refine=True)
            return

        r2bisFace, _ = self.is_facing_target(self.receiver, self.cur_ball[X], self.cur_ball[Y], 4)
        if not r2bisFace:
            self.actions(self.receiver, 'follow', refine=True)
            return
        # if receiver is moving to our goal area
        if self.cur_posture[self.receiver][X] < - 0.8 * self.field[X] / 2:
            if self.cur_posture[self.receiver][X] - self.prev_posture[self.receiver][X] < 0:
                self.actions(self.receiver, 'backward')

        self.actions(self.receiver, 'dribble')
        return

    # let robot with id 'id' execute an action directed by 'mode'
    def actions(self, id, mode = None, target_pts = None, params = None, refine = False):
        if id == None:
            return

        # if the player state is set to 'stop', force the mode to be 'stop'
        if self.player_state[id] == 'stop':
            mode = 'stop'

        if mode == None:
            # reset all robot status
            if self.sender == id:
                self.sender = None
                self.touch = [False, False, False, False, False]
            if self.receiver == id:
                self.receiver = None
            self.player_state[id] = None
            return
        if mode == 'follow':
            # let the robot follow the ball
            if target_pts == None:
                target_pts = self.predict_ball_location(3)
            if params == None:
                params = [1.0, 3.0, 0.6, False]
            if refine:
                self.set_pos_parameters(id, target_pts, params)
            self.set_target_position(id, target_pts[X], target_pts[Y], params[0], params[1], params[2], params[3])
            self.player_state[id] = 'follow'
            return
        if mode == 'dribble':
            # let the robot follow the ball but at a faster speed
            if target_pts == None:
                target_pts = self.cur_ball
            if params == None:
                params = [1.4, 5.0, 0.8, False]
            if refine:
                self.set_pos_parameters(id, target_pts, params)
            self.set_target_position(id, target_pts[X], target_pts[Y], params[0], params[1], params[2], params[3])
            self.player_state[id] = 'dribble'
            return
        if mode == 'kick':
            # kick the ball
            if target_pts == None:
                target_pts = self.cur_ball
            if params == None:
                params = [1.4, 5.0, 0.8, True]
            if self.end_count == 0 and not self.touch[id]:
                self.end_count = self.cur_count + 10 # 0.05 * cnt seconds
            self.player_state[id] = 'kick'
            if self.touch[id]:
                self.player_state[id] = 'stop'
            if not self.touch[id]:
                self.touch[id] = self.cur_posture[id][TOUCH]
            if self.player_state[id] == 'stop':
                params = [0.0, 0.0, 0.0, False]
            self.set_target_position(id, target_pts[X], target_pts[Y], params[0], params[1], params[2], params[3])
            return
        if mode == 'stop':
            # stop while counter is on
            if params == None:
                params = [0.0, 0.0, False]
            self.set_wheel_velocity(id, params[0], params[1], params[2])
            if self.end_count == 0:
                self.end_count = self.cur_count + 5 # 0.05 * cnt seconds
            self.player_state[id] = 'stop'
            if self.end_count - 1 == self.cur_count:
                self.player_state[id] = None
            return
        if mode == 'backward':
            # retreat from the current position
            if target_pts == None:
                target_pts = [self.cur_posture[id][X] + 0.2, self.cur_posture[id][Y]]
            if params == None:
                params = [1.4, 5.0, 0.8, False]
            if refine:
                self.set_pos_parameters(id, target_pts, params)
            self.set_target_position(id, target_pts[X], target_pts[Y], params[0], params[1], params[2], params[3])
            self.player_state[id] = 'backward'
            return
        if mode == 'position':
            # go toward target position
            self.set_target_position(id, target_pts[X], target_pts[Y], params[0], params[1], params[2], params[3])
            return

    def set_pos_parameters(self,id,target_pts,params,mult = 1.2):
        prev_dist = helper.dist(self.prev_posture[id][X],target_pts[X],self.prev_posture[id][Y],target_pts[Y])
        cur_dist = helper.dist(self.cur_posture[id][X],target_pts[X],self.cur_posture[id][Y],target_pts[Y])
        if cur_dist > prev_dist - 0.02:
            params = [params[0] * mult, params[1] * mult, params[2] * mult, params[3]]
        return params

    def is_facing_target(self, id, x, y, div = 4):
        dx = x - self.cur_posture[id][X]
        dy = y - self.cur_posture[id][Y]
        ds = math.sqrt(dx * dx + dy * dy)
        desired_th = (self.cur_posture[id][TH] if (ds == 0) else math.acos(dx / ds))

        theta = self.cur_posture[id][TH]
        if desired_th < 0:
            desired_th += math.pi * 2
        if theta < 0:
            theta += math.pi * 2
        diff_theta = abs(desired_th - theta)
        if diff_theta > math.pi:
            diff_theta = min(diff_theta, math.pi * 2 - diff_theta)
        if diff_theta < math.pi / div or diff_theta > math.pi * (1 -  1 / div):
            return [True, diff_theta]
        return [False, diff_theta]

    def receive_position(self):
        step = 5
        ball_receiver_dist = helper.dist(self.cur_ball[X], self.cur_posture[self.receiver][X], self.cur_ball[Y], \
                                             self.cur_posture[self.receiver][Y])
        prev_ball_receiver_dist = helper.dist(self.prev_ball[X], self.prev_posture[self.receiver][X], \
                                                  self.prev_ball[Y], self.prev_posture[self.receiver][Y])

        diff_dist = prev_ball_receiver_dist - ball_receiver_dist
        if diff_dist > 0:
            step = ball_receiver_dist # diff_dist

        step = min(step, 15)

        predict_pass_point = self.predict_ball_location(step)

        ball_goal_dist = helper.dist(self.cur_ball[X], self.field[X] / 2, self.cur_ball[Y], 0)
        prev_ball_goal_dist = helper.dist(self.prev_ball[X], self.field[X] / 2, self.prev_ball[Y], 0)
        if ball_goal_dist > prev_ball_goal_dist:
            predict_pass_point[X] = predict_pass_point[X] - 0.15

        return predict_pass_point

    def default_rulebased(self, player_list):
        for p in player_list:
            # Add actions instead of default rulebase(goalkeeper, defender, forward) actions
            # If this robot is stuck at field sides, move forward the center
            if pow(self.prev_posture[p][X] - self.cur_posture[p][X],2) + \
                pow(self.prev_posture[p][Y] - self.cur_posture[p][Y],2) < 5e-6:
                if self.cur_posture[p][Y] > 0:
                    self.set_target_position(p, 0, 0, 1.4, 3.5, 0.4, False)
                    continue
            if p == 0:
                self.goalkeeper(0)
                continue
            if p == 1 or p == 2:
                self.defender(p)
                continue
            if p == 3 or p == 4:
                self.forward(p)
                continue

    def pass_play(self, frame, player_list):
        # select only alive player
        _player_list = self.find_active_player(player_list)
        self.cur_count = round(frame.time * 20)  # count = 50 ms

        if self.end_count == self.cur_count:
            self.end_count = 0

        if self.reset_condition():
            self.sender = None
            self.sender_touch = False
            self.receiver = None
        # check if sender exists
        if self.set_sender_condition():
            self.sender = self.set_sender( _player_list)
        # check if receiver exists
        if self.set_receiver_condition():
            self.receiver = self.set_receiver(_player_list)

        if (self.sender != None and self.receiver != None):
            self.pass_ball()
            # if player is sender
            if self.sender in _player_list:
                _player_list.remove(self.sender)
            # if player is receiver
            if self.receiver in _player_list:
                _player_list.remove(self.receiver)

        self.default_rulebased(_player_list)
        return

    def find_active_player(self, ids):
        _ids = []
        for i in ids:
            if self.cur_posture[i][ACTIVE]:
                _ids.append(i)
        return _ids

    def finish(self, frame):
        # save your data if necessary before the program terminates
        print("finish() method called")


if __name__ == '__main__':
    player = RuleBasedA()
    player.run()