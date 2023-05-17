#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

from PIL import Image, ImageTk, ImageDraw

from Setting import Setting

class Coin:
    def __init__(self, setting:Setting, manager, master):
        self.master = master
        self.setting = setting
        self.manager = manager
        self.front_data = setting.coin_front
        self.back_data = setting.coin_back
        self.result = False
        self.rotate = 0
        self.minusFlag = False
        self.font_or_back = True
        self.count = 0
        self.aff = None
        self.stop = False
        self.roll_count = 0

    def createBool(self):
        self.result = random.random() > 0.5

    def rotateUpdate(self):
        if self.rotate == 0:
            self.count += 1
        if self.rotate == 8:
            self.font_or_back = not self.font_or_back
        if self.minusFlag:
            self.rotate -= 1
        else:
            self.rotate += 1
        if self.rotate == 0 or self.rotate == 8:
            self.minusFlag = not self.minusFlag

    def createImage(self, front):
        if front:
            image = self.front_data.copy()
        else:
            image = self.back_data.copy()
        size = image.size
        minus = int(size[1] / 8)
        height = size[1] - minus * self.rotate
        if height < 1:
            height = 1
        image = image.resize((size[0], height))
        if self.count > self.roll_count and self.font_or_back == self.result and image.size[1] == size[1]:
            self.stop = True
        self.image = ImageTk.PhotoImage(image)

    def roll(self):
        self.createImage(self.font_or_back)
        self.manager.field.updateCoin()
        self.rotateUpdate()
        if self.stop:
            self.master.after_cancel(self.aff)
            self.rotate = 0
        else:
            self.aff = self.master.after(8, self.roll)

    def toss(self):
        self.roll_count = random.randint(3, 8)
        self.stop = False
        self.count = 0
        self.createBool()
        if self.aff is not None:
            self.master.after_cancel(self.aff)
        self.roll()


class ShuffleButton:
    def __init__(self, setting:Setting, manager, master):
        self.setting = setting
        self.manager = manager
        self.master = master
        self.image_data = setting.reload_image.resize((setting.card_width, setting.card_width))
        self.rotate = 0
        self.aff = None

    def createImage(self, rotate):
        image = self.image_data.copy()
        image = image.rotate(rotate)
        self.image = ImageTk.PhotoImage(image)

    def shuffle(self):
        self.createImage(self.rotate)
        self.manager.field.updateShuffle()
        self.rotate += 10
        if self.rotate > 360:
            self.master.after_cancel(self.aff)
            self.aff = None
            self.rotate = 0
        else:
            self.aff = self.master.after(8, self.shuffle)

    def shuffleStart(self):
        if self.aff is not None:
            self.master.after_cancel(self.aff)
            self.aff = None
            self.rotate = 0
            self.createImage(self.rotate)
            self.manager.field.updateShuffle()
        else:
            self.shuffle()


class Vstar:
    def __init__(self, setting:Setting, manager):
        self.manager = manager
        self.setting = setting
        self.flag = False
        self.image_data = setting.vstar_image
        self.checkimage_data = setting.vstar_check_image

    def flagUpdate(self, flag=None):
        if flag is None:
            self.flag = not self.flag
        else:
            self.flag = flag
        self.createImage()

    def createImage(self):
        if self.flag:
            image = self.checkimage_data.copy()
            image = image.resize((self.setting.card_height, int(self.setting.card_width*0.8)))
        else:
            image = self.image_data.copy()
            image = image.resize((self.setting.card_height, int(self.setting.card_width*0.8)))
        self.image = ImageTk.PhotoImage(image)


class CheckButton:
    def __init__(self, setting:Setting, systemText):
        self.setting = setting
        self.systemText = systemText
        self.flag = False

    def flagUpdate(self, flag=None):
        if flag is None:
            self.flag = not self.flag
        else:
            self.flag = flag
        self.imageCreate()

    def imageCreate(self):
        image = Image.new("RGBA", (self.setting.card_height, int(self.setting.card_width /3)))
        draw = ImageDraw.Draw(image)
        size = image.size
        x,y = draw.textsize(self.systemText ,self.setting.text_font)
        if self.flag:
            color = "red"
        else:
            color = "white"
        draw.text((size[0]/2 - x/2, size[1]/2 - y/2),
                  self.systemText,
                  font=self.setting.text_font,
                  fill=color,
                  stroke_width=2,
                  stroke_fill='black')
        self.image = ImageTk.PhotoImage(image)
