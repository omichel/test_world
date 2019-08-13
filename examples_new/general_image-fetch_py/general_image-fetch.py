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
        self.ImageBuffer = np.zeros((self.cameraResolution[1], self.cameraResolution[0], 3), dtype=np.uint8)

    def update(self, frame):
        for subimage in frame.subimages:
            x = subimage[0]
            y = subimage[1]
            w = subimage[2]
            h = subimage[3]
            decoded = np.fromstring(base64.b64decode(subimage[4]), dtype=np.uint8)  # convert byte array to numpy array
            image = decoded.reshape((h, w, 4))
            for j in range(h):
                for k in range(w):
                    self.ImageBuffer[j + y, k + x, 0] = image[j, k, 2]  # red channel
                    self.ImageBuffer[j + y, k + x, 1] = image[j, k, 1]  # green channel
                    self.ImageBuffer[j + y, k + x, 2] = image[j, k, 0]  # blue channel
        # Uncomment this part to display the image
        # img = Image.fromarray(self.ImageBuffer, 'RGB')
        # img.show()


if __name__ == '__main__':
    player = ImageFetch()
    player.run()