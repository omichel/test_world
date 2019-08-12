#!/usr/bin/python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

import base64
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../common')
try:
    print(sys.path)
    from participant import Participant
except ImportError as err:
    print('general_image-fetch: \'participant\' module cannot be imported:', err)
    raise


class ImageFetch(Participant):
    def init(self, info):
        self.cameraResolution = info['resolution']
        self.image = [[[0] * self.cameraResolution[1]] * self.cameraResolution[0] * 3]

    def update(self, frame):
        # print(frame.subimages)
        for subimage in frame.subimages:
            decoded = bytes(base64.standard_b64decode(subimage[4]))
            x = subimage[0]
            y = subimage[1]
            w = subimage[2]
            h = subimage[3]
            for i in range(w):
                for j in range(h):
                    self.image[x + i][y + j] = [decoded[4 * (i * h + j)], decoded[4 * (i * h + j) + 1], decoded[4 * (i * h + j) + 2]]


if __name__ == '__main__':
    player = ImageFetch()
    player.run()
