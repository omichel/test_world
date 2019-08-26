#!/usr/bin/env python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

# Additional Information:
# Train Robot 0 to chase the ball from its coordinates, orientation and the ball coordinates
# GameTime and Deadlock duration can be setup on Webots depending on the number of steps and training details

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

class DeepLearningTrain(Participant):
    def init(self, info):
        self.resolution = info['resolution']
        self.max_linear_velocity = info['max_linear_velocity']
        self.colorChannels = 3 # nf
        self.end_of_frame = False
        self.image_buffer = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        self.D = [] # Replay Memory
        self.update_frequency = 100 # Update Target Network
        self.epsilon = 1.0 # Initial epsilon value
        self.final_epsilon = 0.05 # Final epsilon value
        self.dec_epsilon = 0.05 # Decrease rate of epsilon for every generation
        self.step_epsilon = 20000 # Number of iterations for every generation
        self.observation_steps = 5000 # Number of iterations to observe before training every generation
        self.save_every_steps = 5000 # Save checkpoint
        self.num_actions = 11 # Number of possible possible actions
        self._frame = 0
        self._iterations = 0
        self.minibatch_size = 64
        self.gamma = 0.99
        self.sqerror = 100 # Initial sqerror value
        self.Q = NeuralNetwork(None, False, False) # 2nd term: False to start training from scratch, use CHECKPOINT to load a checkpoint
        self.Q_ = NeuralNetwork(self.Q, False, True)
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
                    self.image_buffer[j + y, k + x, 0] = image[j, k, 0] # blue channel
                    self.image_buffer[j + y, k + x, 1] = image[j, k, 1] # green channel
                    self.image_buffer[j + y, k + x, 2] = image[j, k, 2] # red channel

    def update(self, frame):
        # comment the next line if you don't need to use the image information
        self.update_image_buffer(frame.subimages)

        self._frame += 1

        # To get the image at the end of each frame use the variable:
        #self.printConsole(self.image.image_buffer)

        # Reward
        reward = math.exp(-10*(self.distance(frame.coordinates[Frame.MY_TEAM][0][X], frame.coordinates[Frame.BALL][X], \
            frame.coordinates[Frame.MY_TEAM][0][Y], frame.coordinates[Frame.BALL][Y])/4.1))

        # State

        # If you want to use the image as the input for your network
        # You can use pillow: PIL.Image to get and resize the input frame as follows
        #img = Image.fromarray((self.image.image_buffer/255).astype('uint8'), 'RGB') # Get normalized image as a PIL.Image object
        #resized_img = img.resize((NEW_X,NEW_Y))
        #final_img = np.array(resized_img)

        # Example: using the normalized coordinates for robot 0 and ball
        position = [round(frame.coordinates[Frame.MY_TEAM][0][X]/2.05, 2), round(frame.coordinates[Frame.MY_TEAM][0][Y]/1.35, 2), \
                    round(frame.coordinates[Frame.MY_TEAM][0][TH]/(2*math.pi), 2), round(frame.coordinates[Frame.BALL][X]/2.05, 2), \
                    round(frame.coordinates[Frame.BALL][Y]/1.35, 2)]

        # Action
        if np.random.rand() < self.epsilon:
            action = random.randint(0,10)
        else:
            action = self.Q.BestAction(np.array(position)) # using CNNs use final_img as input

        # Set robot wheels
        self.set_action(0, action)
        self.set_speeds(self.wheels)

        # Update Replay Memory
        self.D.append([np.array(position), action, reward])

        # Training!
        if len(self.D) >= self.observation_steps:
            self._iterations += 1
            a = np.zeros((self.minibatch_size, self.num_actions))
            r = np.zeros((self.minibatch_size, 1))
            batch_phy = np.zeros((self.minibatch_size, 5)) # depends on what is your input state
            batch_phy_ = np.zeros((self.minibatch_size, 5)) # depends on what is your input state
            for i in range(self.minibatch_size):
                index = np.random.randint(len(self.D)-1) # Sample a random index from the replay memory
                a[i] = [0 if j !=self.D[index][1] else 1 for j in range(self.num_actions)]
                r[i] = self.D[index][2]
                batch_phy[i] = self.D[index][0].reshape((1,5)) # depends on what is your input state
                batch_phy_[i] = self.D[index+1][0].reshape((1,5)) # depends on what is your input state
            y_value = r + self.gamma*np.max(self.Q_.IterateNetwork(batch_phy_), axis=1).reshape((self.minibatch_size,1))
            self.sqerror = self.Q.TrainNetwork(batch_phy, a, y_value)
            if self._iterations % 100 == 0: # Print information every 100 iterations
                self.printConsole("Squared Error(Episode" + str(self._iterations) + "): " + str(self.sqerror))
                self.printConsole("Epsilon: " + str(self.epsilon))
            if self._iterations % self.update_frequency == 0:
                self.Q_.Copy(self.Q)
                self.printConsole("Copied Target Network")
            if self._iterations % self.save_every_steps == 0:
                self.Q.SaveToFile(CHECKPOINT)
                self.printConsole("Saved Checkpoint")
            if self._iterations % self.step_epsilon == 0:
                self.epsilon = max(self.epsilon - self.dec_epsilon, self.final_epsilon)
                self.D = [] # Reset Replay Memory for new generation
                self.printConsole("New Episode! New Epsilon:" + str(self.epsilon))

    def finish(self, frame):
        # save your data if necessary before the program terminates
        print("finish() method called")


if __name__ == '__main__':
    player = DeepLearningTrain()
    player.run()
