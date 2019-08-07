#!/usr/bin/env python


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

    def update_image(self):
        ret = []
        if self.currentImage is not None:
            self.oldImage = self.currentImage.copy()
        self.currentImage = self.camera.getImageArray()
        xDiv = int(self.width / self.subImageWidth)
        yDiv = int(self.height / self.subImageHeight)
        for y in range(self.subImageWidth):
            for x in range(self.subImageHeight):
                xStart = x * xDiv
                yStart = y * yDiv
                ex = self.width if x == self.subImageWidth - 1 else xStart + xDiv
                ey = self.height if y == self.subImageHeight - 1 else yStart + yDiv

                # compare
                for py in range(yStart, ey):
                    if self.oldImage is None or (self.oldImage[xStart][py] == self.oldImage[ex][py] and self.oldImage[xStart][py] == self.currentImage[xStart][py]):
                        b64_encoded = ''
                        for py in range(yStart, ey):  # TODO: twice py ?!?
                            for px in range(xStart, ex):
                                b64_encoded += base64.b64encode(bytes(self.currentImage[px][py])).decode("utf-8")
                        ret.append([xStart, yStart, ex - xStart, ey - yStart, b64_encoded])
        print(ret)
        ret = []
        return ret
