#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import os

from BattleManager import BattleManager
from CardManager import CardManager
from Setting import Setting

# マリガンカウンター

NAME = "Remote_PokemonCard"
VERSION = "ver.0.1"

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.setting = Setting()
        self.cardManager = CardManager(self.setting)
        self.battleManager = BattleManager(master, self.setting)
        self.aff = None

        master.geometry(f"{self.setting.window_width}x{self.setting.window_height}"+
                        f"+{self.setting.position_x}+{self.setting.position_y}")
        master.title(f"{NAME}_{VERSION}")
        master.bind("<Configure>", lambda event:self.windowResize(master))

        menu_widget = tk.Menu(master)
        master.config(menu=menu_widget)
        select_menu = tk.Menu(menu_widget, tearoff=0)
        setting_menu = tk.Menu(menu_widget, tearoff=0)
        menu_widget.add_command(label="開始",
                                command=lambda:self.start(master))
        menu_widget.add_cascade(label="デッキを選ぶ",
                                menu=select_menu)
        select_menu.add_command(label='デッキコード入力',
                                command=lambda:self.deck_entry_deckID())
        select_menu.add_command(label="ローカルファイルから読み込み",
                                command=lambda:self.deck_entry_local())
        # menu_widget.add_command(label='設定',
        #                         command=lambda:self.setting.createWindow())

    def windowResize(self, master):
        self.setting.window_width = master.winfo_width()
        self.setting.window_height = master.winfo_height()
        self.setting.position_x = master.winfo_x()
        self.setting.position_y = master.winfo_y()
        self.cardManager.reSetting(self.setting)
        self.battleManager.reSetting(self.setting)

    def start(self, master):
        if self.aff is not None:
            self.after_cancel(self.aff)
        self.battleManager.start(self.cardManager.list)
        self.time = [0, 0]
        self.timer(master)

    def deck_entry_deckID(self):
        deck_entry_window = tk.Toplevel()
        deck_entry_window.geometry("300x100")
        deck_entry_window.title("reg")
        deck_entry_box = tk.Entry(deck_entry_window,width=40)
        deck_entry_box.grid(row=0,column=0,pady=5,padx=20)
        paste_button = tk.Button(deck_entry_window,text="貼り付け",command=lambda:clip_paste())
        paste_button.grid(row=1,column=0,pady=5)
        deck_entry_button = tk.Button(deck_entry_window,text="Get!!",command=lambda:submit())
        deck_entry_button.grid(row=2,column=0,pady=5)

        def clip_paste():
            clip = deck_entry_window.clipboard_get()
            deck_entry_box.insert(0,clip)

        def submit():
            deckid = deck_entry_box.get()
            self.cardManager.createDeckOnline(deckid)
            if len(self.cardManager.list) == 60:
                self.cardManager.save()

    def deck_entry_local(self):
        self.deck_image = self.cardManager.createDeckImage()
        window_width = int(self.setting.card_width * 12 / 2)
        window_height = int(self.setting.card_height * 5 / 2)
        image_entry_window = tk.Toplevel()
        image_entry_window.title("デッキ読み込み")
        image_entry_window.geometry(f"{int(window_width+280)}x{int(window_height)+30}")
        frame1 = tk.Frame(image_entry_window)
        frame1.pack(side=tk.LEFT)
        scroll = tk.Scrollbar(frame1)
        deck_list_box = tk.Listbox(frame1,
                                   selectmode="single",
                                   yscrollcommand=scroll.set,
                                   width=40,
                                   height=25)
        deck_list_box.grid(row=0,
                           column=0,
                           sticky=tk.N + tk.S)
        scroll.grid(row=0, column=1,
                    sticky=tk.N + tk.S)
        # select_button = tk.Button(frame1,
        #                           text="SELECT",
        #                           width=20)
        # select_button.grid(row=1, column=0, pady=5)
        scroll["command"]=deck_list_box.yview
        deck_list_box.bind("<<ListboxSelect>>",lambda e:deck_list_click())
        deck_files = os.listdir("Remote_PokemonCard\Deck")
        for num, deck in enumerate(deck_files):
            deck_list_box.insert(num,deck[:-4])

        frame2 = tk.Frame(image_entry_window)
        frame2.pack(side=tk.LEFT)
        deck_code_frame = tk.Frame(frame2)
        deck_code_frame.pack(anchor=tk.W)
        deck_code_text = tk.Label(deck_code_frame,
                                  text="デッキコード")
        deck_code_text.pack(side=tk.LEFT)
        deck_code_box = tk.Entry(deck_code_frame,
                                 width=30)
        deck_code_box.pack(side=tk.LEFT)
        deck_code_copy_button = tk.Button(deck_code_frame,
                                          text="Copy",
                                          command=lambda:clip_copy())
        deck_code_copy_button.pack(side=tk.LEFT, padx=5)
        deck_image_box = tk.Label(frame2,
                                  image=self.deck_image)
        deck_image_box.pack()

        def deck_list_click():
            index = deck_list_box.curselection()
            name = deck_list_box.get(index)
            self.cardManager.createDeckLocal(f"Remote_PokemonCard\Deck\{name}.txt")
            deck_code_box.delete(0, tk.END)
            deck_code_box.insert(0, self.cardManager.deckObj.deckID)
            self.deck_image = self.cardManager.createDeckImage()
            deck_image_box.config(image=self.deck_image)

        def clip_copy():
            image_entry_window.clipboard_clear()
            image_entry_window.clipboard_append(self.cardManager.deckObj.deckID)

    def timer(self, master):
        self.time = [self.time[0], self.time[1]+1]
        if self.time[1] == 60:
            self.time[0] = self.time[0]+1
            self.time[1] = 0
        master.title(f"BattleTimer    {self.time[0]} 分: {self.time[1]} 秒")
        self.aff = self.after(1000, lambda:self.timer(master))

def main():
    win = tk.Tk()
    app = Application(master=win)
    app.mainloop()


if __name__ == "__main__":
    main()
