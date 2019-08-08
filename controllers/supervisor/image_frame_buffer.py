#!/usr/bin/env python

import base64


class ImageFrameBuffer:
    def __init__(self, camera, nx, ny):
        self.camera = camera
        self.width = self.camera.getWidth()
        self.height = self.camera.getHeight()
        self.subImageWidth = nx
        self.subImageHeight = ny
        self.reset()

    def reset(self):
        self.oldImage = None
        self.currentImage = None
        self.lastUpdateTime = None

    def update_image(self, time):
        ret = []
        if self.lastUpdateTime is not None and time - self.lastUpdateTime >= 0.001 * self.camera.getSamplingPeriod():
            return ret
        self.lastUpdateTime = time
        if self.currentImage is not None:
            self.oldImage = self.currentImage
        self.currentImage = self.camera.getImage()
        xDiv = int(self.width / self.subImageWidth)
        yDiv = int(self.height / self.subImageHeight)
        # Loop through sub-images
        for y in range(self.subImageWidth):
            for x in range(self.subImageHeight):
                xStart = x * xDiv
                yStart = y * yDiv
                xEnd = min(xStart + xDiv, self.width)
                yEnd = min(yStart + yDiv, self.height)
                changed = False
                b64_encoded = ''
                # loop through sub-image pixels
                for py in range(yStart, yEnd):
                    for px in range(xStart, xEnd):
                        index = 4 * (yStart * self.width + xStart)
                        b64_encoded += base64.b64encode(bytes(self.currentImage[index:index + 3])).decode("utf-8")
                        if not changed and (self.oldImage is None or self.oldImage[index:index + 3] != self.currentImage[index:index + 3]):
                            changed = True
                if changed:
                    ret.append([xStart, yStart, xEnd - xStart, yEnd - yStart, b64_encoded])
        print(ret)
        ret = []
        return ret
