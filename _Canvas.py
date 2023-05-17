#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random

from PIL import ImageTk, ImageDraw

import Card

class Canvas:
    def __init__(self, master, setting):
        self.setting = setting
        self.list = []
        self.main_canvas = tk.Canvas(master,
                                     width=self.setting.window_width,
                                     height=self.setting.window_height,
                                     bg=self.setting.color)
        self.main_canvas.pack()
        self.main_canvas.bind("<Button-1>", lambda event:self.leftClick(event))
        self.main_canvas.bind("<Button1-Motion>", lambda event:self.mouseDrag(event))
        self.main_canvas.bind("<Button-3>", lambda event:self.rightClick(event))

    def canvasRefresh(self, setting):
        self.setting = setting
        self.main_canvas.config(width=self.setting.window_width,
                                height=self.setting.window_height,
                                bg=self.setting.color)

    def leftClick(self, event):
        self.main_canvas.delete("show_list")
        if 'deck' in dir(self):
            window_list = [self.hand, self.deck, self.temp, self.trash, self.side, self.lost]
            for window in window_list:
                window.play_card_count = 0

        self.tag = self.findIDs(event)
        if self.tag is not None:
            if self.tag[-1] == "current":
                if "system" in self.tag[0]:
                    if "Deck" in self.tag[0]:
                        self.cardMove(self.deck, self.hand)
                    if "Side" in self.tag[0]:
                        self.cardMove(self.side, self.hand)
                    if "Trash" in self.tag[0]:
                        self.trash.showCardList()
                    if "Lost" in self.tag[0]:
                        self.lost.showCardList()
        self.x = event.x
        self.y = event.y

    def rightClick(self, event):
        print("aaa")
        self.tag = self.findIDs(event)
        if self.tag is not None:
            if self.tag[-1] == "current":
                if "system" in self.tag[0]:
                    if "Deck" in self.tag[0]:
                        self.deck.createWindow()
                    if "Side" in self.tag[0]:
                        self.side.createWindow()
                    if "Trash" in self.tag[0]:
                        self.trash.createWindow()
                    if "Lost" in self.tag[0]:
                        self.lost.createWindow()
                    if "Temp" in self.tag[0]:
                        self.temp.createWindow()
                    if "Hand" in self.tag[0]:
                        self.hand.createWindow()

    def mouseDrag(self, event):
        if not "system" in self.tag[0]:
            if self.tag[-1] == "current":
                self.main_canvas.move(self.tag[0],
                                    event.x - self.x,
                                    event.y - self.y)
                self.x = event.x
                self.y = event.y

    def findIDs(self, event):
        closest_ids = self.main_canvas.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.main_canvas.gettags(closest_ids[0])
            return tag

    def cardMove(self, source, destination, count=1):
        for i in range(count):
            destination.list.append(source.list.pop(0))
        source.systemImageUpdate()
        source.canvasUpdate()
        destination.systemImageUpdate()
        destination.canvasUpdate()

    def start(self, card_id_list):
        if len(card_id_list) != 60:
            print("デッキ読み込みエラー")
        else:
            self.windowDestroy()
            self.deck = CanvasSystemDeck(self.main_canvas, self.setting, "Deck", card_id_list, self.list)
            self.deck.systemImagePositionUpdate((self.setting.window_width, 0, "ne"))
            self.deck.systemImageUpdate()
            self.deck.geometryUpdate(self.setting.card_width*8,
                                     self.setting.card_height*4,
                                     self.setting.position_x,
                                     self.setting.position_y)
            self.hand = CanvasSystemHand(self.main_canvas, self.setting, "Hand", self.list)
            self.hand.systemImagePositionUpdate((int(self.setting.window_width /4), self.setting.window_height, "sw"))
            self.hand.systemImageUpdate()
            self.hand.geometryUpdate(self.setting.window_width,
                                     self.setting.card_height,
                                     self.setting.position_x,
                                     self.setting.position_y + self.setting.window_height)
            self.temp = CanvasSystemTemp(self.main_canvas, self.setting, "Temp", self.list)
            self.temp.systemImagePositionUpdate((int(self.setting.window_width /4 *3), self.setting.window_height, "se"))
            self.temp.systemImageUpdate()
            self.temp.geometryUpdate(self.setting.card_width*7,
                                     self.setting.card_height,
                                     self.setting.position_x,
                                     self.setting.position_y)
            self.trash = CanvasSystemTrash(self.main_canvas, self.setting, "Trash", self.list)
            self.trash.systemImagePositionUpdate((self.setting.window_width, self.setting.window_height, "se"))
            self.trash.systemImageUpdate()
            self.trash.geometryUpdate(self.setting.card_width*8,
                                      self.setting.card_height*4,
                                      self.setting.position_x,
                                      self.setting.position_y)
            self.lost = CanvasSystemLost(self.main_canvas, self.setting, "Lost", self.list)
            self.lost.systemImagePositionUpdate((0, 0, "nw"))
            self.lost.systemImageUpdate()
            self.lost.geometryUpdate(self.setting.card_width*10,
                                     self.setting.card_height,
                                     self.setting.position_x,
                                     self.setting.position_y)
            self.side = CanvasSystemSide(self.main_canvas, self.setting, "Side", self.list)
            self.side.systemImagePositionUpdate((0, self.setting.window_height, "sw"))
            self.side.systemImageUpdate()
            self.side.geometryUpdate(self.setting.card_width*7,
                                     self.setting.card_height,
                                     self.setting.position_x,
                                     self.setting.position_y)
            self.deck.shuffle()
            self.cardMove(self.deck, self.hand, count=7)
            self.cardMove(self.deck, self.side, count=6)
            self.hand.createWindow()

    def windowDestroy(self):
        self.main_canvas.delete("all")
        if 'deck' in dir(self):
            window_list = [self.hand, self.deck, self.temp, self.trash, self.side, self.lost]
            for window in window_list:
                window.windowClose()


class CanvasSystem:
    def __init__(self, main_canvas:tk.Canvas, setting, systemText, fieldList:list):
        self.main_canvas = main_canvas
        self.setting = setting
        self.viewFlag = False
        self.systemText = systemText
        self.list = []
        self.window = None
        self.play_card_count = 0
        self.fieldList = fieldList

    def geometryUpdate(self, window_width=None, window_height=None, position_x=None, position_y=None):
        if window_width is not None:
            self.window_width = window_width
        if window_height is not None:
            self.window_height = window_height
        if position_x is not None:
            self.position_x = position_x
        if position_y is not None:
            self.position_y = position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def systemImagePositionUpdate(self, position):
        self.canvas_position = position

    def sort(self):
        self.list.sort()

    def createWindow(self):
        self.viewFlag = True
        self.systemImageUpdate()
        self.windowClose()
        self.window = tk.Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self.windowClose)
        self.window.title(self.systemText)
        self.window.geometry(self.geometry)
        self.createCanvas()
        self.canvasUpdate()

    def createCanvas(self):
        self.canvas = tk.Canvas(self.window,
                                width=self.window_width,
                                height=self.window_height,
                                bg=self.setting.color)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda event:self.leftClick(event))
        self.canvas.bind("<Button-3>", lambda event:self.rightClick(event))

    def systemImageUpdate(self):
        self.main_canvas.delete(f"system_{self.systemText}")
        image = self.setting.card_back_image.copy()
        draw = ImageDraw.Draw(image)
        self.drawSystemText(draw)
        self.drawLength(draw)
        self.image = ImageTk.PhotoImage(image)
        self.main_canvas.delete(f"system_{self.systemText}")
        self.main_canvas.create_image(self.canvas_position[0],
                                      self.canvas_position[1],
                                      anchor=self.canvas_position[2],
                                      image=self.image,
                                      tag=f"system_{self.systemText}")

    def drawSystemText(self, draw):
        x, _ = draw.textsize(self.systemText, self.setting.text_font)
        if self.viewFlag:
            color = "red"
        else:
            color = "white"
        draw.text((int(self.setting.card_width/2 - x/2), 0),
                    self.systemText,
                    font=self.setting.text_font,
                    fill=color,
                    stroke_width=3,
                    stroke_fill="black")

    def drawLength(self, draw):
        x, y = draw.textsize(str(len(self.list)), self.setting.count_font)
        draw.text((int(self.setting.card_width/2 - x/2),
                   int(self.setting.card_height/2 - y/2)),
                   str(len(self.list)),
                   font=self.setting.count_font,
                   fill="white",
                   stroke_width=3,
                   stroke_fill='black')

    def windowClose(self):
        if self.window is not None:
            self.geometry = self.window.geometry()
            self.window.destroy()
            self.window = None
            self.viewFlag = False

    def canvasUpdate(self):
        print(f"{self.systemText}_canvasUpdate_未実装")

    def findIDs(self, event):
        closest_ids = self.canvas.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.canvas.gettags(closest_ids[0])
            return tag

    def leftClick(self, event):
        tag = self.findIDs(event)
        if tag[-1] == "current":
            for card in self.list:
                if f"tag_{card.deckID}" == tag[0]:
                    break
            self.list.remove(card)
            self.fieldList.append(card)
            self.canvasUpdate()
            self.main_canvas.create_image(self.setting.window_width/2 + self.setting.card_width/2 * self.play_card_count,
                                        self.setting.window_height - self.setting.card_height,
                                        anchor="c",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")
            self.play_card_count += 1
            self.systemImageUpdate()

    def rightClick(self, event):
        print(f"{self.systemText}_rightClick_未実装")

    def showCardList(self):
        new_line_index = self.setting.window_width // self.setting.card_width * 2 -1
        for index, card in enumerate(self.list):
            row = index // new_line_index
            if row > 0:
                index = index - row * new_line_index
            self.main_canvas.create_image(index * (self.setting.card_width /2),
                                          row * self.setting.card_height,
                                          anchor="nw",
                                          image=card.image,
                                          tag="show_list")



class CanvasSystemDeck(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, card_id_list, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)
        self.list = [Card.Card(cardID, num) for num, cardID in enumerate(card_id_list)]
        for card in self.list:
            card.image_create(self.setting.card_width, self.setting.card_height, self.setting.text_font)

    def shuffle(self):
        random.shuffle(self.list)

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            for index, card in enumerate(self.list):
                row = index // 15
                if row > 0:
                    index = index - row * 15
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        row * self.setting.card_height,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")


class CanvasSystemHand(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)

    def createWindow(self):
        if self.setting.card_width * len(self.list) >= self.window_width:
            self.geometryUpdate(window_width=self.setting.card_width * len(self.list))
        else:
            self.geometryUpdate(window_width=self.setting.window_width)
        super().createWindow()

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            self.canvas.config(width=self.window_width,
                            height=self.window_height)
            for index, card in enumerate(self.list):
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        0,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")


class CanvasSystemTemp(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            for index, card in enumerate(self.list):
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        0,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")


class CanvasSystemTrash(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            for index, card in enumerate(self.list):
                row = index // 15
                if row > 0:
                    index = index - row * 15
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        row * self.setting.card_height,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")

class CanvasSystemSide(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            for index, card in enumerate(self.list):
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        0,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")

class CanvasSystemLost(CanvasSystem):
    def __init__(self, main_canvas, setting, systemText, field_list):
        super().__init__(main_canvas, setting, systemText, field_list)

    def createWindow(self):
        if len(self.list) > 10:
            self.geometryUpdate(window_height=self.setting.card_height*2)
        super().createWindow()

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            self.canvas.config(width=self.window_width,
                            height=self.window_height)
            for index, card in enumerate(self.list):
                self.canvas.create_image(index * (self.setting.card_width /2),
                                        0,
                                        anchor="nw",
                                        image=card.image,
                                        tag=f"tag_{card.deckID}")