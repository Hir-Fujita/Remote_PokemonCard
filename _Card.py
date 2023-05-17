#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import tkinter as tk
from tkinter import filedialog

import requests
import re
from bs4 import BeautifulSoup
import io
from PIL import Image, ImageTk, ImageDraw

import Canvas


def ImageAlpha(image):
    size = image.size
    mask = Image.open("Remote_PokemonCard\Image\mask.png").convert('L').resize(size)
    new_image = image.copy()
    new_image.putalpha(mask)
    return new_image

class Card:
    def __init__(self, CardID, deckID):
        self.deckID = deckID
        if os.path.isdir(f"Remote_PokemonCard/Card/{CardID}"):
            filename = os.listdir(f"Remote_PokemonCard/Card/{CardID}")[0]
            self.image_data = Image.open(f"Remote_PokemonCard/Card/{CardID}/{filename}")
            if filename[0:5] == "ポケモン_":
                self.hp = 0
            else:
                self.hp = None
            self.name = filename.split("_")[1].replace(".jpg", "")
        else:
            self.hp = None
            os.makedirs(f"Remote_PokemonCard/Card/{CardID}")
            r = requests.get(f"https://www.pokemon-card.com/card-search/details.php/card/{CardID}")
            soup = BeautifulSoup(r.text,"html.parser")
            card_name = re.findall(r'<h1 class="Heading1 mt20">(.*)</h1>',str(soup))[0]
            card_type = re.findall(r'<h2 class="mt20">(.*)</h2>',str(soup))[0]
            if card_type == "ワザ" or card_type == "特性":
                card_type = "ポケモン"
                self.type = 0
            find_start = r'class="fit" src="'
            find_end = r'\d*"/>'
            image_url = re.findall(rf'{find_start}(.*){find_end}',str(soup))
            image_url = image_url[0]
            image = Image.open(
                io.BytesIO(requests.get(f"https://www.pokemon-card.com{image_url}").content))
            image = image.resize((300,420))
            image.save(f"Remote_PokemonCard/Card/{CardID}/{card_type}_{card_name}.jpg", quality=95)
            self.name = card_name
            self.image_data = image
            print(f"completed:{card_name}")

    def __lt__(self, other):
        return self.deckID < other.deckID

    def __repr__(self):
        return repr((self.deckID, self.name))

    def image_create(self, width, height, font):
        image = self.image_data.resize((width, height))
        if self.hp is not None:
            draw = ImageDraw.Draw(image)
            x,y = draw.textsize(str(self.hp) ,font)
            draw.text((width -x -(width /20), height -y -(height /20)),
                      str(self.hp),
                      font=font,
                      fill="white",
                      stroke_width=2,
                      stroke_fill='black')
        image = ImageAlpha(image)
        self.image = ImageTk.PhotoImage(image)

    def hpPlus(self):
        self.hp = self.hp +10

    def hpMinus(self):
        self.hp = self.hp -10
        if self.hp < 0:
            self.hp = 0

class DeckData:
    def __init__(self):
        self.cardID_list = []
        self.deckID = ""

    def deck_create_deckID(self, deckID):
        self.deckID = deckID
        self.cardID_list = []
        r = requests.get(f"https://www.pokemon-card.com/deck/result.html/deckID/{deckID}/")
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
                        self.cardID_list.append(card)

    def deck_create_localfile(self, filepath):
        self.cardID_list = []
        with open(filepath, "r", encoding="utf-8") as f:
            loaddata = f.read().split("\n")
        self.cardID_list = loaddata[0:60]
        self.deckID = loaddata[-1]

    def save(self):
        filepath = filedialog.asksaveasfilename(title='デッキ保存',
                                                defaultextension='.txt',
                                                filetypes=[("Text Files", ".txt")],
                                                initialdir = "Remote_PokemonCard\Deck")
        if filepath != "":
            with open(filepath, "w", encoding="utf-8") as f:
                for card_id in self.cardID_list:
                    f.writelines(f"{card_id}\n")
                f.writelines(self.deckID)

    def create_deck_image(self, card_width, card_height, resize=False, blank=False):
        if resize:
            width = int(card_width / 2)
            height = int(card_height / 2)
        else:
            width = int(card_width)
            height = int(card_height)
        if blank:
            image = Image.new("RGBA", (width*12, height*5), ("green"))
        else:
            image = Image.new("RGBA", (width*12, height*5), (0,0,0,0))
            for num, cardID in enumerate(self.cardID_list):
                if num < 12:
                    h = 0
                    w = num * width
                elif num < 24:
                    h = height * 1
                    w = (num - 12) * width
                elif num < 36:
                    h = height * 2
                    w = (num - 24) * width
                elif num < 48:
                    h = height * 3
                    w = (num - 36) * width
                else:
                    h = height * 4
                    w = (num - 48) * width
                card_image = Card(cardID, num).image_data.resize((width, height))
                card_image = ImageAlpha(card_image)
                image.paste(card_image, (w,h))
        image = ImageTk.PhotoImage(image)
        return image

# class BattleDeckData(DeckData):
#     def __init__(self, card_id_list, setting):
#         self.setting = setting
#         self.deck = Canvas.CanvasSystem(self.setting,
#                                  "Deck")
#         self.deck.list = [Card(cardID, num) for num, cardID in enumerate(card_id_list)]
#         self.hand = Canvas.CanvasSystemHand(self.setting,
#                                      "Hand",
#                                      False)
#         self.temp = Canvas.CanvasSystemTemp(self.setting,
#                                  "Temp")
#         self.trash = Canvas.CanvasSystem(self.setting,
#                                   "Trash")
#         self.lost = Canvas.CanvasSystem(self.setting,
#                                  "Lost")
#         self.side = Canvas.CanvasSystem(self.setting,
#                                  "Side")
#         self.field = []

#     def shuffle(self):
#         random.shuffle(self.deck.list)

#     def canvas_update(self):
#         self.deck.image_update()
#         self.hand.image_update()
#         self.temp.image_update()
#         self.trash.image_update()
#         self.lost.image_update()
#         self.side.image_update()

#     def start(self):
#         self.shuffle()
#         self.draw(count=7)
#         for i in range(6):
#             self.side.list.append(self.deck.list.pop(0))
#         self.canvas_update()

#     def draw(self, count=1):
#         for i in range(count):
#             self.hand.list.append(self.deck.list.pop(0))

