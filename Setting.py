#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import colorchooser

from PIL import Image, ImageFont, ImageDraw, ImageTk

class Setting:
    # アプリケーションの設定クラス
    def __init__(self):
        if os.path.isfile(f"Remote_PokemonCard/setting.pkl"):
            pass
        else:
            self.position_x = 100
            self.position_y = 100
            self.window_width = 1200
            self.window_height = 700

            self.card_width = 120
            self.card_height = int(self.card_width * 1.4)
            self.color = "green"
            self.alphaValue = 200
            font_path = "Remote_PokemonCard/Image/Molot.ttf"
            font_size = int(self.card_width / 2)
            font_size_2 = int(self.card_width / 3)
            self.count_font = ImageFont.truetype(font_path, font_size)
            self.text_font = ImageFont.truetype(font_path, font_size_2)
            self.mask = Image.open("Remote_PokemonCard/Image/mask.png").convert('L')
            self.card_back_image = self.ImageAlpha(self.ImageOpen("Remote_PokemonCard/Image/card.png"))
            self.check_image = Image.open("Remote_PokemonCard/Image/check.png").convert("RGBA")
            self.coin_front = self.ellipseImage(Image.open("Remote_PokemonCard/Image/coin_front.png"))
            self.coin_back = self.ellipseImage(Image.open("Remote_PokemonCard/Image/coin_back.png"))
            self.system_card_image = self.rectImage(self.ImageOpen("Remote_PokemonCard/Image/card.png"))
            self.reload_image = Image.open("Remote_PokemonCard/Image/reload.png")
            self.doku_image = Image.open("Remote_PokemonCard/Image/doku.png").convert("RGBA")
            self.yakedo_image = Image.open("Remote_PokemonCard/Image/yakedo.png").convert("RGBA")
            self.mahi_image = Image.open("Remote_PokemonCard/Image/mahi.png").convert("RGBA")
            self.nemuri_image = Image.open("Remote_PokemonCard/Image/nemuri.png").convert("RGBA")
            self.konran_image = Image.open("Remote_PokemonCard/Image/konran.png").convert("RGBA")
            self.vstar_image = Image.open("Remote_PokemonCard/Image/Vstar.png").convert("RGBA")
            self.vstar_check_image = Image.open("Remote_PokemonCard/Image/Vstar_check.png").convert("RGBA")

    def settingWindowImageCreate(self):
        self.tk_card_back_image = ImageTk.PhotoImage(self.card_back_image)

    def ImageOpen(self, imagepath):
        image = Image.open(imagepath)
        new_image = image.resize((self.card_width, self.card_height))
        return new_image

    def ImageAlpha(self, image:Image.Image):
        size = image.size
        mask = self.mask.resize(size)
        new_image = image.copy()
        new_image.putalpha(mask)
        return new_image

    def SystemImage(self, image:Image.Image):
        new_image = image.copy()
        new_image.putalpha(self.alphaValue)
        return new_image

    def rectImage(self, image:Image.Image):
        image = image.copy()
        image = self.SystemImage(image)
        size = image.size
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0, 0),
                        (size[0]-1, size[1]-1)],
                        outline="black",
                        width=4)
        return image

    def ellipseImage(self, image:Image.Image):
        image = image.copy().resize((self.card_width, self.card_width))
        size = image.size
        draw = ImageDraw.Draw(image)
        draw.ellipse([(1, 1), (size[0]-1, size[1]-1)], outline="black", width=4)
        mask = Image.new("L", (size[0], size[1]), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse([(1, 1), (size[0]-1, size[1]-1)], fill=255)
        image.putalpha(mask)
        image.resize((self.card_width, self.card_width))
        return image

    def create_color_image(self):
        image = Image.new("RGBA", (self.card_width, self.card_height), self.color)
        self.color_image = ImageTk.PhotoImage(image)

    def createWindow(self, update):
        self.window = tk.Toplevel()
        self.window.geometry(f"{int(self.window_width /2)}x{int(self.window_height /2)}+{self.position_x}+{self.position_y}")
        self.window.title("設定")

        back_image_frame = tk.Frame(self.window)
        back_image_frame.grid(row=0, column=0)
        back_image_button = tk.Button(back_image_frame, text="裏側画像")
        back_image_button.pack()
        self.card_back_image_tk = ImageTk.PhotoImage(self.card_back_image)
        back_image_button = tk.Label(back_image_frame, image=self.card_back_image_tk)
        back_image_button.pack()

        canvas_color_frame = tk.Frame(self.window)
        canvas_color_frame.grid(row=0, column=1, padx=5)
        canvas_color_button = tk.Button(canvas_color_frame, text="キャンバスの色",
                                        command=lambda:change_color())
        canvas_color_button.pack()
        self.create_color_image()
        canvas_color_label = tk.Label(canvas_color_frame,
                                      image=self.color_image)
        canvas_color_label.pack()

        def change_color():
            color = colorchooser.askcolor()
            if color != (None, None):
                print(color)
                self.color = color[-1]
                update.reSetting()



