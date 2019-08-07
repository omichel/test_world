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
        for iy in range(self.subImageWidth):
            for ix in range(self.subImageHeight):
                bx = int(ix * (self.width / self.subImageWidth))  # begin x
                by = int(iy * (self.height / self.subImageHeight))  # begin y
                ex = self.width if ix == self.subImageWidth - 1 else int(bx + (self.width / self.subImageWidth))
                ey = self.height if iy == self.subImageHeight - 1 else int(by + (self.height / self.subImageHeight))

                # compare
                for py in range(by, ey):
                    if self.oldImage is None or (self.oldImage[bx][py] == self.oldImage[ex][py] and self.oldImage[bx][py] == self.currentImage[bx][py]):
                        b64_encoded = ""
                        for py in range(by, ey):  # TODO: twice py ?!?
                            for px in range(bx, ex):
                                b64_encoded += base64.b64encode(bytes(self.currentImage[px][py])).decode("utf-8") 
                        ret.append([bx, by, ex - bx, ey - by, b64_encoded])
        return ret
