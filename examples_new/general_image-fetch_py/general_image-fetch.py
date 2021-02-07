#!/usr/bin/env python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

import base64
import numpy as np

import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../common')
try:
    from participant import Participant, Game, Frame
except ImportError as err:
    print('general_image-fetch: \'participant\' module cannot be imported:', err)
    raise

class ImageFetch(Participant):
    def init(self, info):
        self.resolution = info['resolution']
        self.image_buffer = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)

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
        self.update_image_buffer(frame.subimages)

        # display the received image
        cv2.imshow('image', self.image_buffer / 255.0)
        cv2.waitKey(1)

    def finish(self, frame):
        # save your data if necessary before the program terminates
        print("finish() method called")


if __name__ == '__main__':
    participant = ImageFetch()
    participant.run()
