#!/usr/bin/python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

import base64
import numpy as np
from PIL import Image
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
        self.ImageBuffer = np.zeros((self.cameraResolution[1], self.cameraResolution[0], 3))

    def update(self, frame):
        for subimage in frame.subimages:
            decoded = map(ord, bytes(base64.b64decode(subimage[4])))
            x = subimage[0]
            y = subimage[1]
            w = subimage[2]
            h = subimage[3]
            for i in range(w):
                for j in range(h):
                    index = 4 * (i * h + j)
                    self.ImageBuffer[y + j][x + i] = decoded[index:index + 3]
            # img = Image.fromarray(self.ImageBuffer, 'RGB')
            # img.show()

if __name__ == '__main__':
    player = ImageFetch()
    player.run()
