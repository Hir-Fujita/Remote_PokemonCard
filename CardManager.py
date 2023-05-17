#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tkinter import filedialog

import requests
import re
from bs4 import BeautifulSoup
import io
from PIL import Image, ImageTk, ImageDraw

from Setting import Setting

class CardManager:
    def __init__(self, setting:Setting):
        self.list = []
        self.setting = setting
        self.deckObj = Deck()

    def reSetting(self, setting:Setting):
        self.setting = setting

    def createDeckOnline(self, officialDeckID):
        self.deckObj.createDeckOnline(officialDeckID)
        self.list = [Card(card, index, self.setting) for index, card in enumerate(self.deckObj.list)]

    def createDeckLocal(self, filepath):
        self.deckObj.createDeckLocal(filepath)
        self.list = [Card(card, index, self.setting) for index, card in enumerate(self.deckObj.list)]

    def save(self):
        filepath = filedialog.asksaveasfilename(title='デッキ保存',
                                                defaultextension='.txt',
                                                filetypes=[("Text Files", ".txt")],
                                                initialdir = "Remote_PokemonCard\Deck")
        if filepath != "":
            with open(filepath, "w", encoding="utf-8") as f:
                for cardID in self.deckObj.list:
                    f.writelines(f"{cardID}\n")
                f.writelines(self.deckObj.deckID)

    def createDeckImage(self):
        width = int(self.setting.card_width / 2)
        height = int(self.setting.card_height / 2)
        image = Image.new("RGBA", (width*12, height*5), self.setting.color)
        for num, card in enumerate(self.list):
            row = num // 12
            if num > 0:
                num = num - row * 12
            card_image = card.image_data.copy().resize((width, height))
            card_image = self.setting.ImageAlpha(card_image)
            image.paste(card_image,
                        (num * width,
                         row * height))
        image = ImageTk.PhotoImage(image)
        return image


class Deck:
    def __init__(self):
        self.list = []
        self.deckID = ""

    def __repr__(self):
        return repr((f"{len(self.list)}枚", f"DeckID:{self.deckID}"))

    def createDeckOnline(self, officialDeckID):
        self.deckID = officialDeckID
        self.list = []
        r = requests.get(f"https://www.pokemon-card.com/deck/result.html/deckID/{self.deckID}/")
        soup = BeautifulSoup(r.text,"html.parser")
        find_start = r'"deck_.*" type="hidden" value="'
        find_end = r'\d*">'
        card_list_data = re.findall(rf'{find_start}(.*){find_end}',str(soup))
        for card_lists in card_list_data:
            card_lists = str(card_lists).split("-")
            if card_lists != [""]:
                for card in card_lists:
                    card_data = card.split("_")
                    CardID = card_data[1]
                    card = card_data[0]
                    for i in range(int(CardID)):
                        self.list.append(card)

    def createDeckLocal(self, filepath):
        self.list = []
        with open(filepath, "r", encoding="utf-8") as f:
            loaddata = f.read().split("\n")
        self.list = loaddata[0:60]
        self.deckID = loaddata[-1]


class Card:
    def __init__(self, cardID, index, setting:Setting):
        self.check = False
        self.back_image = False
        self.doku = False
        self.yakedo = False
        self.bad_stat = ""
        self.setting = setting
        self.index = index
        if os.path.isdir(f"Remote_PokemonCard/Card/{cardID}"):
            filename = os.listdir(f"Remote_PokemonCard/Card/{cardID}")[0]
            self.image_data = Image.open(f"Remote_PokemonCard/Card/{cardID}/{filename}")
            if filename[0:5] == "ポケモン_":
                self.hp = 0
            else:
                self.hp = None
            self.name = filename.split("_")[1].replace(".jpg", "")
        else:
            os.makedirs(f"Remote_PokemonCard/Card/{cardID}")
            r = requests.get(f"https://www.pokemon-card.com/card-search/details.php/card/{cardID}")
            soup = BeautifulSoup(r.text,"html.parser")
            card_name = re.findall(r'<h1 class="Heading1 mt20">(.*)</h1>',str(soup))[0]
            card_type = re.findall(r'<h2 class="mt20">(.*)</h2>',str(soup))[0]
            if card_type == "ワザ" or card_type == "特性":
                card_type = "ポケモン"
                self.type = 0
            else:
                self.hp = None
            find_start = r'class="fit" src="'
            find_end = r'\d*"/>'
            image_url = re.findall(rf'{find_start}(.*){find_end}',str(soup))
            image_url = image_url[0]
            image = Image.open(
                io.BytesIO(requests.get(f"https://www.pokemon-card.com{image_url}").content))
            image = image.resize((500, 700))
            image.save(f"Remote_PokemonCard/Card/{cardID}/{card_type}_{card_name}.jpg", quality=95)
            self.name = card_name
            self.image_data = image
            print(f"completed:{card_name}")

    def reSetting(self, setting:Setting):
        self.setting = setting

    def __lt__(self, other):
        return self.index < other.index

    def __repr__(self):
        return repr((self.index, self.name))

    def reset(self):
        if self.hp is not None:
            self.hp = 0
        self.check = False
        self.back_image = False
        self.doku = False
        self.yakedo = False
        self.bad_stat = ""
        self.imageCreate()

    def hpPlus(self):
        self.hp = self.hp +10
        self.imageCreate()

    def hpMinus(self):
        self.hp = self.hp -10
        if self.hp < 0:
            self.hp = 0
        self.imageCreate()

    def setCheck(self, flag=None):
        if flag is None:
            self.check = not self.check
        elif flag == "hold":
            pass
        elif flag:
            self.check = True
        else:
            self.check = False
        self.imageCreate()

    def backImage(self, flag=False):
        if flag:
            self.back_image = True
        else:
            self.back_image = False
        self.imageCreate()

    def badStatSet(self, name):
        if name == "どく":
            self.doku = not self.doku
        if name == "やけど":
            self.yakedo = not self.yakedo
        if name == self.bad_stat:
            self.bad_stat = ""
        else:
            self.bad_stat = name
        self.imageCreate()

    def imageCreate(self):
        if not self.back_image:
            image = self.image_data.resize((self.setting.card_width, self.setting.card_height))
            if self.hp is not None:
                draw = ImageDraw.Draw(image)
                x,y = draw.textsize(str(self.hp) ,self.setting.count_font)
                draw.text((self.setting.card_width -x -(self.setting.card_width /20),
                        self.setting.card_height -y -(self.setting.card_height /20)),
                        str(self.hp),
                        font=self.setting.count_font,
                        fill="white",
                        stroke_width=2,
                        stroke_fill='black')
            if self.check:
                check_image = self.setting.check_image.copy()
                check_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                       Image.LANCZOS)
                image.paste(check_image,
                            (self.setting.card_width - int(self.setting.card_width /3),0),
                            mask=check_image)
            if self.doku:
                doku_image = self.setting.doku_image.copy()
                doku_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                      Image.LANCZOS)
                image.paste(doku_image,
                            (0, 0),
                            mask=doku_image)
            if self.yakedo:
                yakedo_image = self.setting.yakedo_image.copy()
                yakedo_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                        Image.LANCZOS)
                image.paste(yakedo_image,
                            (int(self.setting.card_width /3), 0),
                            mask=yakedo_image)
            if self.bad_stat == "ねむり":
                nemuri_image = self.setting.nemuri_image.copy()
                nemuri_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                        Image.LANCZOS)
                image.paste(nemuri_image,
                            (0, int(self.setting.card_width /3)),
                            mask=nemuri_image)
            if self.bad_stat == "まひ":
                mahi_image = self.setting.mahi_image.copy()
                mahi_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                        Image.LANCZOS)
                image.paste(mahi_image,
                            (0, int(self.setting.card_width /3)),
                            mask=mahi_image)
            if self.bad_stat == "こんらん":
                konran_image = self.setting.konran_image.copy()
                konran_image.thumbnail((int(self.setting.card_width /3), int(self.setting.card_width /3)),
                                        Image.LANCZOS)
                image.paste(konran_image,
                            (0, int(self.setting.card_width /3)),
                            mask=konran_image)
        else:
            image = self.setting.card_back_image.resize((self.setting.card_width, self.setting.card_height))
        image = self.setting.ImageAlpha(image)
        self.image = ImageTk.PhotoImage(image)
