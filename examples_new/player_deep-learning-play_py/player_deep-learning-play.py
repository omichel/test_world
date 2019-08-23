#!/usr/bin/env python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../common')
try:
    from participant import Participant, Game, Frame
except ImportError as err:
    print('player_skeleton: \'participant\' module cannot be imported:', err)
    raise

import math
import random
import base64
import numpy as np

#from PIL import Image
from dqn_nn import NeuralNetwork

# shortcuts
X = Frame.X
Y = Frame.Y
TH = Frame.TH
ACTIVE = Frame.ACTIVE
TOUCH = Frame.TOUCH

#path to your checkpoint
CHECKPOINT = os.path.join(os.path.dirname(__file__), 'dqn.ckpt')

class DeepLearningPlay(Participant):
    def init(self, info):
        self.resolution = info['resolution']
        self.max_linear_velocity = info['max_linear_velocity']
        self.colorChannels = 3 # nf
        self.end_of_frame = False
        self.ImageBuffer = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        self._frame = 0
        self.Q = NeuralNetwork(None, CHECKPOINT, False) # 2nd term: False to start training from scratch, use CHECKPOINT to load a checkpoint
        self.wheels = [0 for _ in range(10)]

    def set_action(self, robot_id, action_number):
        if action_number == 0:
            self.wheels[2*robot_id] = 0.75
            self.wheels[2*robot_id + 1] = 0.75
            # Go Forward with fixed velocity
        elif action_number == 1:
            self.wheels[2*robot_id] = 0.75
            self.wheels[2*robot_id + 1] = 0.5
            # Turn
        elif action_number == 2:
            self.wheels[2*robot_id] = 0.75
            self.wheels[2*robot_id + 1] = 0.25
            # Turn
        elif action_number == 3:
            self.wheels[2*robot_id] = 0.75
            self.wheels[2*robot_id + 1] = 0
            # Turn
        elif action_number == 4:
            self.wheels[2*robot_id] = 0.5
            self.wheels[2*robot_id + 1] = 75
            # Turn
        elif action_number == 5:
            self.wheels[2*robot_id] = 0.25
            self.wheels[2*robot_id + 1] = 0.75
            # Turn
        elif action_number == 6:
            self.wheels[2*robot_id] = 0
            self.wheels[2*robot_id + 1] = 0.75
            # Turn
        elif action_number == 7:
            self.wheels[2*robot_id] = -0.75
            self.wheels[2*robot_id + 1] = -0.75
            # Go Backward with fixed velocity
        elif action_number == 8:
            self.wheels[2*robot_id] = -0.1
            self.wheels[2*robot_id + 1] = 0.1
            # Spin
        elif action_number == 9:
            self.wheels[2*robot_id] = 0.1
            self.wheels[2*robot_id + 1] = -0.1
            # Spin
        elif action_number == 10:
            self.wheels[2*robot_id] = 0
            self.wheels[2*robot_id + 1] = 0
            # Do not move

    def distance(self, x1, x2, y1, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

    def update_image_buffer(self, subimages):
        for subimage in subimages:
            x = subimage[0]
            y = subimage[1]
            w = subimage[2]
            h = subimage[3]
            decoded = np.fromstring(base64.b64decode(subimage[4]), dtype=np.uint8) # convert byte array to numpy array
            image = decoded.reshape((h, w, 4))
            for j in range(h):
                for k in range(w):
                    self.ImageBuffer[j + y, k + x, 0] = image[j, k, 0] # blue channel
                    self.ImageBuffer[j + y, k + x, 1] = image[j, k, 1] # green channel
                    self.ImageBuffer[j + y, k + x, 2] = image[j, k, 2] # red channel

    def update(self, frame):
        # comment the next line if you don't need to use the image information
        self.update_image_buffer(frame.subimages)

        self._frame += 1

        # To get the image at the end of each frame use the variable:
        #self.printConsole(self.image.ImageBuffer)

        # Reward
        reward = math.exp(-10*(self.distance(frame.coordinates[Frame.MY_TEAM][0][X], frame.coordinates[Frame.BALL][X], \
            frame.coordinates[Frame.MY_TEAM][0][Y], frame.coordinates[Frame.BALL][Y])/4.1))

        # State

        # If you want to use the image as the input for your network
        # You can use pillow: PIL.Image to get and resize the input frame as follows
        #img = Image.fromarray((self.image.ImageBuffer/255).astype('uint8'), 'RGB') # Get normalized image as a PIL.Image object
        #resized_img = img.resize((NEW_X,NEW_Y))
        #final_img = np.array(resized_img)

        # Example: using the normalized coordinates for robot 0 and ball
        position = [round(frame.coordinates[Frame.MY_TEAM][0][X]/2.05, 2), round(frame.coordinates[Frame.MY_TEAM][0][Y]/1.35, 2), \
                    round(frame.coordinates[Frame.MY_TEAM][0][TH]/(2*math.pi), 2), round(frame.coordinates[Frame.BALL][X]/2.05, 2), \
                    round(frame.coordinates[Frame.BALL][Y]/1.35, 2)]

        # Action
        action = self.Q.BestAction(np.array(position)) # using CNNs use final_img as input

        # Set robot wheels
        self.set_action(0, action)
        self.set_speeds(self.wheels)

    def finish(self, frame):
        # save your data if necessary before the program terminates
        print("finish() method called")


if __name__ == '__main__':
    player = DeepLearningPlay()
    player.run()
