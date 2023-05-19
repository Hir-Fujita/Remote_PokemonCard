#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random

from PIL import ImageDraw, ImageTk

from Setting import Setting
import SystemObject

FIELD = 0
DECK = 1
HAND = 2
TRASH = 3
TEMP = 4
LOST = 5
SIDE = 6

class BattleManager:
    def __init__(self, master, setting:Setting):
        self.setting = setting
        self.field = FieldSystem(master, setting, self)
        self.big_system = BigImageSystem(setting, "BIGIMAGE", self)
        self.coin = SystemObject.Coin(setting, self, master)
        self.shuffleButton = SystemObject.ShuffleButton(setting, self, master)
        self.vstar = SystemObject.Vstar(setting, self)
        self.energy = SystemObject.CheckButton(setting, "Energy")
        self.support = SystemObject.CheckButton(setting, "Support")
        self.retreat = SystemObject.CheckButton(setting, "Retreat")
        self.big_image = None

    def reSetting(self, setting:Setting):
        self.setting = setting
        if "systemList" in dir(self):
            for system in self.systemList:
                system.reSetting(setting)
        else:
            self.field.reSetting(setting)

    def start(self, cardManagerList):
        self.list = cardManagerList.copy()
        if len(self.list) == 60:
            if "systemList" in dir(self):
                for i in range(7):
                    if i != 0:
                        self.systemList[i].closeWindow()
            self.field.canvas.delete("all")
            self.field.list.clear()
            self.deck = DeckSystem(self.setting, "Deck", self)
            self.hand = HandSystem(self.setting, "Hand", self)
            self.trash = TrashSystem(self.setting, "Trash", self)
            self.temp = TempSystem(self.setting, "Temp", self)
            self.lost = LostSystem(self.setting, "Lost", self)
            self.side = SideSystem(self.setting, "Side", self)
            self.systemList = [self.field, self.deck, self.hand, self.trash, self.temp, self.lost, self.side]
            self.deck.list = self.list.copy()
            for card in self.deck.list:
                card.reset()
            self.deck.shuffle()
            self.cardMove(DECK, HAND, count=7)
            self.cardMove(DECK, SIDE, count=6)
            for i in range(7):
                self.systemImageUpdate(i)
            self.hand.createWindow()
            self.createObject()
        else:
            print("ERROR:デッキの枚数が不正です")

    def createObject(self):
        self.coin.createImage(True)
        self.field.updateCoin()
        self.shuffleButton.createImage(0)
        self.field.updateShuffle()
        self.vstar.flagUpdate(False)
        self.field.updateVstar()
        self.energy.flagUpdate(False)
        self.support.flagUpdate(False)
        self.retreat.flagUpdate(False)
        self.field.updateCheckButton()

    def systemImageUpdate(self, subject):
        if not subject == FIELD:
            system = self.systemList[subject]
            system.imageUpdate()
            system.canvasUpdate()
            self.field.canvas.delete(f"system_{system.systemText}")
            self.field.canvas.create_image(system.systemPosition[0],
                                        system.systemPosition[1],
                                        anchor=system.systemPosition[2],
                                        image=system.image,
                                        tag=f"system_{system.systemText}")

    def cardMove(self, source, destination, count=1, card=None, returnTop=False):
        source_list = self.systemList[source].list
        destination_list = self.systemList[destination].list
        if card is None:
            for i in range(count):
                destination_list.append(source_list.pop(0))
        else:
            if isinstance(card, list):
                for c in card:
                    if returnTop:
                        destination_list.insert(0, c)
                    else:
                        destination_list.append(c)
                    source_list.remove(c)
            else:
                if returnTop:
                    destination_list.insert(0, card)
                else:
                    destination_list.append(card)
                source_list.remove(card)
        self.systemImageUpdate(source)
        self.systemImageUpdate(destination)
        if source == FIELD:
            self.cardReset(destination)

    def cardReset(self, subject):
        reset_list = self.systemList[subject].list
        for card in reset_list:
            card.reset()
        if self.systemList[subject].window is not None:
            self.systemList[subject].canvasUpdate()

    def showCardList(self, subject):
        system = self.systemList[subject]
        new_line_index = self.setting.window_width // self.setting.card_width * 2 -1
        for index, card in enumerate(system.list):
            row = index // new_line_index
            if row > 0:
                index = index - row * new_line_index
            self.field.canvas.create_image(index * (self.setting.card_width /2),
                                           row * self.setting.card_height,
                                           anchor="nw",
                                           image=card.image,
                                           tag="show_image")

    def fieldCardSet(self, card, backImage=False):
        self.field.list.append(card)
        if backImage:
            card.imageCreate(backImage=True)
        self.field.canvas.create_image(self.setting.window_width/2 + (self.setting.card_width/2 * self.field.playcount),
                                       self.setting.window_height - self.setting.card_height,
                                       anchor="c",
                                       image=card.image,
                                       tag=f"id_{card.index}")
        self.field.playcount += 1
        self.field.canvasUpdate()

    def showBigImage(self, card):
        self.big_image = ImageTk.PhotoImage(self.setting.ImageAlpha(card.image_data))
        self.field.canvas.create_image(0,0,
                                       image=self.big_image,
                                       anchor="nw",
                                       tag="show_image")

    def showBigImageWindow(self, card):
        self.big_system.createWindow(card)

    def coinToss(self):
        self.coin.toss()

    def deckShuffle(self):
        self.deck.shuffle()
        self.shuffleButton.shuffleStart()

class FieldSystem:
    def __init__(self, master, setting:Setting, manager:BattleManager):
        self.manager = manager
        self.setting = setting
        self.list = []
        self.playcount = 0
        self.tag = None
        self.canvas = tk.Canvas(master,
                                width=self.setting.window_width,
                                height=self.setting.window_height,
                                bg=self.setting.color)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda event:self.leftClick(event))
        self.canvas.bind("<Button1-Motion>", lambda event:self.mouseDrag(event))
        self.canvas.bind("<Button-3>", lambda event:self.rightClick(event))
        self.canvas.bind("<ButtonRelease-1>", lambda event:self.mouseRelease(event))
        self.canvas.bind("<MouseWheel>",lambda event:self.mouseWheel(event))
        self.canvas.bind("<Double-Button-1>", lambda event:self.doubleClick(event))
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(label="どく",
                              command=lambda:self.findCard(update=True, badstat="どく", check="hold"))
        self.menu.add_command(label="やけど",
                              command=lambda:self.findCard(update=True, badstat="やけど", check="hold"))
        self.menu.add_command(label="まひ",
                              command=lambda:self.findCard(update=True, badstat="まひ", check="hold"))
        self.menu.add_command(label="ねむり",
                              command=lambda:self.findCard(update=True, badstat="ねむり", check="hold"))
        self.menu.add_command(label="こんらん",
                              command=lambda:self.findCard(update=True, badstat="こんらん", check="hold"))
        self.menu.add_command(label="画像表示",
                              command=lambda:self.manager.showBigImage(self.findCard()))
        self.menu.add_command(label="画像表示(Window)",
                              command=lambda:self.manager.showBigImageWindow(self.findCard()))

    def reSetting(self, setting:Setting):
        self.setting = setting
        self.canvas.config(width=self.setting.window_width,
                           height=self.setting.window_height,
                           bg=self.setting.color)
        if self.manager.coin.image is not None:
            self.updateCoin()
            self.updateShuffle()
            self.updateVstar()
            self.updateCheckButton()
            tags = self.getTagAll()
            for tag in tags:
                self.cardReplace(tag)


    def leftClick(self, event):
        self.canvas.delete("show_image")
        self.playcount = 0
        self.tag = self.findTag(event)
        if self.tag is not None:
            if self.tag[-1] == "current":
                if "system" in self.tag[0]:
                    if "Deck" in self.tag[0]:
                        self.manager.deck.mulligan_update(-1)
                        self.manager.cardMove(DECK, HAND)
                    if "Side" in self.tag[0]:
                        self.manager.cardMove(SIDE, HAND)
                    if "Temp" in self.tag[0]:
                        self.manager.cardMove(DECK, TEMP)
                    if "Trash" in self.tag[0]:
                        self.manager.showCardList(TRASH)
                    if "Lost" in self.tag[0]:
                        self.manager.showCardList(LOST)
                    if "Coin" in self.tag[0]:
                        self.manager.coinToss()
                    if "Shuffle" in self.tag[0]:
                        self.manager.deckShuffle()
                        if self.manager.deck.window is not None:
                            self.manager.deck.canvasUpdate()
                    if "Vstar" in self.tag[0]:
                        self.manager.vstar.flagUpdate()
                        self.updateVstar()
                    if self.manager.energy.systemText in self.tag[0]:
                        self.manager.energy.flagUpdate()
                        self.updateCheckButton()
                    if self.manager.support.systemText in self.tag[0]:
                        self.manager.support.flagUpdate()
                        self.updateCheckButton()
                    if self.manager.retreat.systemText in self.tag[0]:
                        self.manager.retreat.flagUpdate()
                        self.updateCheckButton()
                else:
                    self.canvas.addtag_withtag("move", self.tag[0])
                    self.tag = self.findTag(event)
                    self.canvasUpdate()
        self.x = event.x
        self.y = event.y

    def rightClick(self, event):
        self.canvas.delete("show_image")
        self.tag = self.findTag(event)
        if self.tag is not None:
            if self.tag[-1] == "current":
                if "system" in self.tag[0]:
                    if "Deck" in self.tag[0]:
                        self.manager.deck.createWindow()
                    if "Hand" in self.tag[0]:
                        self.manager.hand.createWindow()
                    if "Side" in self.tag[0]:
                        self.manager.side.createWindow()
                    if "Temp" in self.tag[0]:
                        self.manager.temp.createWindow()
                    if "Trash" in self.tag[0]:
                        self.manager.trash.createWindow()
                    if "Lost" in self.tag[0]:
                        self.manager.lost.createWindow()
                elif self.findCard().back_image:
                    self.findCard(update=True, check=False, back=False)
                else:
                    self.menu.post(event.x_root, event.y_root)

    def mouseDrag(self, event):
        if self.tag is not None:
            if "move" in self.tag:
                self.canvas.move("move",
                                event.x - self.x,
                                event.y - self.y)
                self.x = event.x
                self.y = event.y
            elif self.tag[-1] != "current" or self.tag[0] == "system_bg":
                self.canvas.delete("rect")
                self.canvas.create_rectangle(self.x, self.y, event.x, event.y,
                                            outline="red", tag="rect")

    def mouseRelease(self, event):
        if self.tag is not None:
            move_list = []
            for card in self.list:
                for tag in self.getTagAll():
                    if "move" in tag and f"id_{card.index}" == tag[0]:
                        move_list.append(card)
            if ("rect", "current") in self.getTagAll():
                self.canvas.addtag_overlapping("move", self.x, self.y, event.x, event.y)
                for tag in self.getTagAll():
                    if "system" in tag[0]:
                        self.canvas.dtag(tag[0], "move")
                self.canvas.delete("rect")
            else:
                for tag in self.getTagAll():
                    if "move" in tag:
                        self.cardReplace(tag)
                self.canvas.dtag("move", "move")

            tag = self.findTag(event)
            if tag[-1] == "current":
                if "system" in tag[0]:
                    if len(move_list) != 0:
                        if "Deck" in tag[0]:
                            self.manager.cardMove(FIELD, DECK, card=move_list)
                            self.deleteCardImage(move_list)
                        if "Hand" in tag[0]:
                            self.manager.cardMove(FIELD, HAND, card=move_list)
                            self.deleteCardImage(move_list)
                        if "Trash" in tag[0]:
                            self.manager.cardMove(FIELD, TRASH, card=move_list)
                            self.deleteCardImage(move_list)
                        if "Temp" in tag[0]:
                            self.manager.cardMove(FIELD, TEMP, card=move_list)
                            self.deleteCardImage(move_list)
                        if "Lost" in tag[0]:
                            self.manager.cardMove(FIELD, LOST, card=move_list)
                            self.deleteCardImage(move_list)
                        if "Side" in tag[0]:
                            self.manager.cardMove(FIELD, SIDE, card=move_list)
                            self.deleteCardImage(move_list)

    def cardReplace(self, tag):
        x, y, x_end, y_end = self.canvas.bbox(tag[0])
        if x < 0:
            self.canvas.move(tag[0], -x, 0)
        if y < 0:
            self.canvas.move(tag[0], 0, -y)
        if x_end > self.setting.window_width:
            self.canvas.move(tag[0], self.setting.window_width - x_end, 0)
        if y_end > self.setting.window_height:
            self.canvas.move(tag[0], 0, self.setting.window_height - y_end)

    def mouseWheel(self, event):
        tag = self.findTag(event)
        if tag[-1] == "current":
            if not "system" in tag[0]:
                for card in self.list:
                    if f"id_{card.index}" == tag[0]:
                        break
                if card.hp is not None:
                    x, y, _, _ = self.canvas.bbox(tag[0])
                    self.canvas.delete(tag[0])
                    if event.delta > 0:
                        card.hpPlus()
                    else:
                        card.hpMinus()
                    self.canvas.create_image(x, y, image=card.image,
                                             anchor="nw", tag=f"id_{card.index}")
            elif tag[0] == "system_Deck":
                self.manager.deck.mulligan_update(event.delta)

    def doubleClick(self, event):
        tag = self.findTag(event)
        if tag[-1] == "current" and not tag[0] == "system_bg":
            if "system" in tag[0]:
                if "Deck" in tag[0]:
                    self.manager.deck.mulligan_update(-1)
                    self.manager.cardMove(DECK, HAND)
                if "Side" in tag[0]:
                    self.manager.cardMove(SIDE, HAND)
                if "Temp" in tag[0]:
                    self.manager.cardMove(DECK, TEMP)
                if "Trash" in tag[0]:
                    self.manager.showCardList(TRASH)
                if "Lost" in tag[0]:
                    self.manager.showCardList(LOST)
            else:
                self.tag = tag
                self.findCard(True, check=None, back=False)
        else:
            self.turnReset()

    def cardImageUpdate(self, card, reset=False, check=None, back=False, badstat=""):
        x, y, _, _ = self.canvas.bbox(f"id_{card.index}")
        self.canvas.delete(f"id_{card.index}")
        if reset:
            card.reset()
        card.setCheck(check)
        card.backImage(back)
        if badstat != "":
            card.badStatSet(badstat)
        self.canvas.create_image(x, y, image=card.image,
                                 anchor="nw", tag=f"id_{card.index}")
        self.canvasUpdate()

    def findCard(self, update=False, reset=False, check=None, back=False, badstat=""):
        for card in self.list:
            if self.tag[0] == f"id_{card.index}":
                if update:
                    break
                return card
        self.cardImageUpdate(card, reset, check, back, badstat)

    def turnReset(self):
        for tag in self.getTagAll():
            for card in self.list:
                if tag[0] == f"id_{card.index}":
                    x, y, _, _ = self.canvas.bbox(tag[0])
                    card.setCheck(False)
                    self.canvas.delete(f"id_{card.index}")
                    self.canvas.create_image(x, y, image=card.image,
                                             anchor="nw", tag=f"id_{card.index}")
        self.manager.energy.flagUpdate(False)
        self.manager.support.flagUpdate(False)
        self.manager.retreat.flagUpdate(False)
        self.updateCheckButton()
        self.canvasUpdate()

    def findTag(self, event):
        closest_ids = self.canvas.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.canvas.gettags(closest_ids[0])
            return tag

    def getTagAll(self):
        id_list = list(self.canvas.find_all())
        tag_list = [self.canvas.gettags(id) for id in id_list]
        return tag_list

    def canvasUpdate(self):
        if self.tag is not None:
            for card in self.list:
                if self.tag[0] == f"id_{card.index}":
                    if card.hp is None:
                        self.canvas.lower(f"id_{card.index}")
                    else:
                        self.canvas.lift(f"id_{card.index}")
                    break
        for tag in self.getTagAll():
            if "system" in tag[0]:
                self.canvas.lift(tag[0])

    def deleteCardImage(self, cardlist:list):
        for card in cardlist:
            self.canvas.delete(f"id_{card.index}")

    def updateCoin(self):
        self.canvas.delete("system_Coin")
        self.canvas.create_image(self.setting.card_width*1.7,
                                 self.setting.card_height/2,
                                 image=self.manager.coin.image,
                                 anchor="c",
                                 tag="system_Coin")

    def updateShuffle(self):
        self.canvas.delete("system_Shuffle")
        self.canvas.create_image(self.setting.window_width,
                                 self.setting.card_height,
                                 image=self.manager.shuffleButton.image,
                                 anchor="ne",
                                 tag="system_Shuffle")

    def updateVstar(self):
        self.canvas.delete("system_Vstar")
        self.canvas.create_image(self.setting.window_width - int(self.setting.card_width*1.1),
                                 0,
                                 image=self.manager.vstar.image,
                                 anchor="ne",
                                 tag="system_Vstar")

    def updateCheckButton(self):
        row = int(self.setting.card_width /3)
        self.canvas.delete(f"system_{self.manager.energy.systemText}")
        self.canvas.create_image(self.setting.window_width - int(self.setting.card_width*1.1),
                                 int(self.setting.card_width*0.8),
                                 image=self.manager.energy.image,
                                 anchor="ne",
                                 tag=f"system_{self.manager.energy.systemText}")
        self.canvas.delete(f"system_{self.manager.support.systemText}")
        self.canvas.create_image(self.setting.window_width - int(self.setting.card_width*1.1),
                                 int(self.setting.card_width*0.8)+row,
                                 image=self.manager.support.image,
                                 anchor="ne",
                                 tag=f"system_{self.manager.support.systemText}")
        self.canvas.delete(f"system_{self.manager.retreat.systemText}")
        self.canvas.create_image(self.setting.window_width - int(self.setting.card_width*1.1),
                                 int(self.setting.card_width*0.8)+row*2,
                                 image=self.manager.retreat.image,
                                 anchor="ne",
                                 tag=f"system_{self.manager.retreat.systemText}")





class ChildSystem:
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        self.manager = manager
        self.setting = setting
        self.systemText = systemText
        self.window = None
        self.viewFlag = False
        self.list = []
        self.systemPosition = (0, 0, 0)
        self.system = None
        self.canvas = None

    def reSetting(self, setting:Setting):
        self.setting = setting

    def __repr__(self):
        return repr(f"SystemClass:{self.systemText}")

    def sort(self):
        self.list.sort()
        self.canvasUpdate()

    def addCommand(self):
        self.menu = tk.Menu(self.canvas, tearoff=0)

    def insertCommand(self):
        self.menu.add_command(label="ソート",
                              command=lambda:self.sort())
        self.menu.add_command(label="画像表示",
                              command=lambda:self.manager.showBigImage(self.findCard()))
        self.menu.add_command(label="画像表示(Window)",
                              command=lambda:self.manager.showBigImageWindow(self.findCard()))

    def shuffle(self):
        random.shuffle(self.list)

    def findTag(self, event):
        closest_ids = self.canvas.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.canvas.gettags(closest_ids[0])
            return tag

    def findCard(self):
        for card in self.list:
            if self.tag[0] == f"id_{card.index}":
                return card

    def imageUpdate(self):
        image = self.setting.system_card_image.copy()
        draw = ImageDraw.Draw(image)
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
        x, y = draw.textsize(str(len(self.list)), self.setting.count_font)
        draw.text((int(self.setting.card_width/2 - x/2),
                   int(self.setting.card_height/2 - y/2)),
                   str(len(self.list)),
                   font=self.setting.count_font,
                   fill="white",
                   stroke_width=3,
                   stroke_fill='black')
        self.image = ImageTk.PhotoImage(image)

    def createWindow(self):
        self.closeWindow()
        self.viewFlag = True
        self.manager.systemImageUpdate(self.system)
        self.window = tk.Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.window.title(self.systemText)
        self.window.geometry(self.geometry)
        self.canvas = tk.Canvas(self.window,
                                width=self.window_width,
                                height=self.window_height,
                                bg=self.setting.color)
        self.canvas.pack()
        self.addCommand()
        self.canvasUpdate()
        self.canvas.bind("<Button-1>", lambda event:self.leftClick(event))
        self.canvas.bind("<Button-3>", lambda event:self.rightClick(event))

    def closeWindow(self):
        if self.window is not None:
            self.geometryUpdate()
            self.window.destroy()
            self.window = None
            self.viewFlag = False
            self.manager.systemImageUpdate(self.system)

    def geometryUpdate(self):
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.position_x = self.window.winfo_x()
        self.position_y = self.window.winfo_y()
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def canvasUpdate(self):
        if self.window is not None:
            self.canvas.delete("all")
            new_line_index = self.window_width // self.setting.card_width * 2 -1
            for index, card in enumerate(self.list):
                row = index // new_line_index
                if row > 0:
                    index = index - row * new_line_index
                self.canvas.create_image(index * (self.setting.card_width /2),
                                         row * self.setting.card_height,
                                         anchor="nw",
                                         image=card.image,
                                         tag=f"id_{card.index}")

    def leftClick(self, event):
        tag = self.findTag(event)
        if tag is not None:
            if tag[-1] == "current":
                for card in self.list:
                    if tag[0] == f"id_{card.index}":
                        self.tag = tag
                        break
                self.list.remove(card)
                self.manager.fieldCardSet(card)
                self.manager.systemImageUpdate(self.system)

    def rightClick(self, event):
        tag = self.findTag(event)
        if tag[-1] == "current":
            self.tag = tag
            self.menu.post(event.x_root, event.y_root)


class DeckSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = DECK
        self.systemPosition = (setting.window_width, 0, "ne")
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*4
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        if self.canvas is not None:
            self.canvas.config(bg=self.setting.color)
        self.mulligan_count = 0

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.systemPosition = (setting.window_width, 0, "ne")
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*4
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)

    def mulligan_update(self, delta):
        if delta > 0:
            self.mulligan_count +=1
        else:
            self.mulligan_count -=1
            if self.mulligan_count < 0:
                self.mulligan_count = 0
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)

    def imageUpdate(self):
        image = self.setting.system_card_image.copy()
        draw = ImageDraw.Draw(image)
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
        x, y = draw.textsize(str(len(self.list)), self.setting.count_font)
        draw.text((int(self.setting.card_width/2 - x/2),
                   int(self.setting.card_height/2 - y/2)),
                   str(len(self.list)),
                   font=self.setting.count_font,
                   fill="white",
                   stroke_width=3,
                   stroke_fill='black')
        if self.mulligan_count != 0:
            x, y = draw.textsize(str(self.mulligan_count), self.setting.count_font)
            draw.text((int(self.setting.card_width - x - 2),
                       int(self.setting.card_height - y - 2)),
                       str(self.mulligan_count),
                       font=self.setting.count_font,
                       fill="red",
                       stroke_width=3,
                       stroke_fill='black')
        self.image = ImageTk.PhotoImage(image)

    def addCommand(self):
        super().addCommand()
        self.menu.add_command(label="ハンドに入れる",
                              command=lambda:self.manager.cardMove(DECK, HAND, card=self.findCard()))
        self.menu.add_command(label="Tempにいれる",
                              command=lambda:self.manager.cardMove(DECK, TEMP, card=self.findCard()))
        super().insertCommand()

    def closeWindow(self):
        if self.window is not None:
            self.shuffle()
        super().closeWindow()


class HandSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = HAND
        self.systemPosition = (int(self.setting.window_width /4), self.setting.window_height, "sw")
        self.window_width = setting.window_width
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y + setting.window_height
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.systemPosition = (int(self.setting.window_width /4), self.setting.window_height, "sw")
        self.window_width = setting.window_width
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y + setting.window_height
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)
        if self.canvas is not None:
            self.canvas.config(bg=self.setting.color)

    def addCommand(self):
        super().addCommand()
        self.menu.add_command(label="裏向きで場に出す",
                              command=lambda:[self.findCard().backImage(True),
                                              self.manager.fieldCardSet(self.findCard()),
                                              self.list.remove(self.findCard()),
                                              self.manager.systemImageUpdate(self.system)])
        self.menu.add_command(label="デッキに戻す",
                              command=lambda:self.manager.cardMove(HAND, DECK, card=self.findCard()))
        self.menu.add_command(label="すべてデッキに戻す",
                              command=lambda:[self.shuffle(),
                                              self.manager.cardMove(HAND, DECK, count=len(self.list))])
        self.menu.add_command(label="すべて場に出す",
                              command=lambda:self.allField())
        self.menu.add_command(label="Tempにいれる",
                              command=lambda:self.manager.cardMove(HAND, TEMP, card=self.findCard()))
        super().insertCommand()

    def allField(self):
        for card in self.list:
            self.manager.fieldCardSet(card)
        self.list = []
        self.imageUpdate()
        self.canvasUpdate()
        self.manager.systemImageUpdate(HAND)

class TrashSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = TRASH
        self.systemPosition = (self.setting.window_width, self.setting.window_height, "se")
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*4
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.systemPosition = (self.setting.window_width, self.setting.window_height, "se")
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*4
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)
        if self.window is not None:
            self.canvas.config(bg=self.setting.color)

    def addCommand(self):
        super().addCommand()
        super().insertCommand()


class TempSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = TEMP
        self.systemPosition = (int(self.setting.window_width /4 *3), self.setting.window_height, "se")
        self.window_width = setting.card_width*7
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.systemPosition = (int(self.setting.window_width /4 *3), self.setting.window_height, "se")
        self.window_width = setting.card_width*7
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)
        if self.canvas is not None:
            self.canvas.config(bg=self.setting.color)

    def addCommand(self):
        super().addCommand()
        self.menu.add_command(label="ハンドに入れる",
                              command=lambda:[self.manager.cardMove(TEMP, HAND, card=self.findCard()),
                                              self.closeCheck()])
        self.menu.add_command(label="すべてハンドに入れる",
                              command=lambda:[self.manager.cardMove(TEMP, HAND, count=len(self.list)),
                                              self.closeCheck()])
        self.menu.add_command(label="デッキの上に戻す",
                              command=lambda:[self.manager.cardMove(TEMP, DECK, card=self.findCard(), returnTop=True),
                                              self.closeCheck()])
        self.menu.add_command(label="デッキの下に戻す",
                              command=lambda:[self.manager.cardMove(TEMP, DECK, card=self.findCard()),
                                              self.closeCheck()])
        self.menu.add_command(label="すべてデッキに戻す",
                              command=lambda:[self.manager.cardMove(TEMP, DECK, card=self.findCard()),
                                              self.closeCheck()])
        super().insertCommand()

    def leftClick(self, event):
        super().leftClick(event)
        self.closeCheck()

    def closeCheck(self):
        if len(self.list) == 0:
            self.closeWindow()


class SideSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = SIDE
        self.systemPosition = (0, self.setting.window_height, "sw")
        self.window_width = setting.card_width*6
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.systemPosition = (0, self.setting.window_height, "sw")
        self.window_width = setting.card_width*6
        self.window_height = setting.card_height
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)
        if self.canvas is not None:
            self.canvas.config(bg=self.setting.color)

    def addCommand(self):
        super().addCommand()
        self.menu.add_command(label="Handにいれる",
                              command=lambda:self.manager.cardMove(SIDE, HAND, card=self.findCard()))
        super().insertCommand()

    def closeWindow(self):
        self.shuffle()
        super().closeWindow()


class LostSystem(ChildSystem):
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        super().__init__(setting, systemText, manager)
        self.system = LOST
        self.systemPosition = (0, 0, "nw")
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*2
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def reSetting(self, setting: Setting):
        super().reSetting(setting)
        self.window_width = setting.card_width*8
        self.window_height = setting.card_height*2
        self.position_x = setting.position_x
        self.position_y = setting.position_y
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
        self.imageUpdate()
        self.manager.systemImageUpdate(self.system)
        if self.canvas is not None:
            self.canvas.config(bg=self.setting.color)

    def addCommand(self):
        super().addCommand()
        super().insertCommand()


class BigImageSystem:
    def __init__(self, setting:Setting, systemText, manager:BattleManager):
        self.manager = manager
        self.setting = setting
        self.systemText = systemText
        self.window = None
        self.window_width = 500
        self.window_height = 700
        self.position_x = 0
        self.position_y = 0
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"

    def createWindow(self, card):
        if self.window is not None:
            self.closeWindow()
        self.window = tk.Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.window.title(self.systemText)
        self.window.geometry(self.geometry)
        self.canvas = tk.Canvas(self.window,
                                width=self.window_width,
                                height=self.window_height,
                                bg=self.setting.color)
        self.image = ImageTk.PhotoImage(self.setting.ImageAlpha(card.image_data))
        self.canvas.create_image(0,0,
                                 image=self.image,
                                 anchor="nw",
                                 tag="show_image")
        self.canvas.pack()

    def closeWindow(self):
        if self.window is not None:
            self.canvas.delete("show_image")
            self.geometryUpdate()
            self.window.destroy()
            self.window = None
            self.viewFlag = False

    def geometryUpdate(self):
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.position_x = self.window.winfo_x()
        self.position_y = self.window.winfo_y()
        self.geometry = f"{self.window_width}x{self.window_height}+{self.position_x}+{self.position_y}"
