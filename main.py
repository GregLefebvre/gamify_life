from pprint import pprint
from win32gui import GetWindowText, GetForegroundWindow
import time
import pyautogui
import json
import os
import datetime
import keyboard
import pygame
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from tkinter.messagebox import *
from win10toast import ToastNotifier
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

pygame.init()

def send_toast(str, substr=""):
    toaster = ToastNotifier()
    toaster.show_toast(str, substr, icon_path=None, duration=2, threaded=True)

def get_active_window():
    active_win_data = GetWindowText(GetForegroundWindow())
    active_win_title = active_win_data
    applications = ["Google Chrome", "Adobe Acrobat Reader DC", "console", "Discord", "Command Prompt",
                    "Mail", "Calendar", "Mozilla Firefox", "Microsoft​ Edge"]
    for app in applications:
        if app in active_win_data:
            active_win_title = app
    if active_win_title == "console":
        active_win_title = "Command Prompt"
    elif active_win_title == "C:":
        active_win_title = "File explorer"
    return active_win_title, active_win_data

def remove_substr_from_str(substr, str):
    res = str
    if substr in str:
        for i in range(len(str)):
            if str[i:i+len(substr)] == substr:
                res = str[:i]+str[min(i+len(substr), len(str)):]
    return res

def get_daily_tasks():
    file_days = os.listdir("json_days")
    today = str(datetime.date.today())
    file_name = today+".json"
    file_path = "json_days/"+file_name
    daily_tasks = list()
    if file_name in file_days:
        with open(file_path, 'r') as f:
            data = json.load(f)
        daily_tasks = data["tasks"]
    return daily_tasks

def three_digits_number(n):
    n = str(n)
    while len(n) < 3:
        n = "0"+n
    return n

def two_digits_number(n):
    n = str(n)
    while len(n) < 2:
        n = "0"+n
    return n

def readable_times(hours, minutes, seconds):
    if minutes+hours+seconds == 0:
        return "0s"
    else:
        s = seconds%60
        m = (minutes+seconds//60)%60
        h = hours + (minutes+seconds//60)//60
        return two_digits_number(h)+":"+two_digits_number(m)+":"+two_digits_number(s)


def encode_cesar(string, decalage):
    minusules = "abcdefghijklmnopqrstuvwxyz"
    majuscules = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    for letter in string:
        if letter in minusules:
            ind = minusules.index(letter)
            ind = (ind+decalage)%26
            res_letter = minusules[ind]
        elif letter in majuscules:
            ind = majuscules.index(letter)
            ind = (ind+decalage)%26
            res_letter = majuscules[ind]
        else:
            res_letter = letter
        res = res+res_letter
    return res

def decode_cesar(string, decalage):
    return encode_cesar(string, -decalage)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, bg1=False, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        if bg1:
            self.canvas = tk.Canvas(self, bg=bg1, highlightthickness=0, relief='ridge')
            self.scrollable_frame = tk.Frame(self.canvas, bg=bg1)
        else:
            self.canvas = tk.Canvas(self, highlightthickness=0, relief='ridge')
            self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.rowconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize_frame)
        scrollbar.pack(side="right", fill="y")

    def resize_frame(self, e):
        self.canvas.itemconfig(self.win, width=self.canvas.winfo_width()-4)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/100)), "units")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.today = str(datetime.date.today())

        self.title_font = tkfont.Font(family='Arial', size=18, weight="bold")
        self.subtitle_font = tkfont.Font(family='Arial', size=14, weight="bold")
        self.category_font = tkfont.Font(family='Arial', size=12, weight="bold")
        self.daily_category_font = tkfont.Font(family='Arial', size=12, weight="bold")
        self.normal_font = tkfont.Font(family='Arial', size=12)
        self.duration_font = tkfont.Font(family='Arial', size=18)
        self.citation_font = tkfont.Font(family='Arial', size=18, weight="bold")

        l1 = str(int(pyautogui.size()[1]*0.8))
        l0 = str(int(pyautogui.size()[0]*0.6))
        self.geometry(l0+'x'+l1+'+20+20')
        self.title("gamify_life")
        self.resizable(True, True)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be SOLID above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DailyPage, TaskPage, AddTaskPage, BreakPage, StatsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DailyPage")
        self.current_frame = "DailyPage"
        #block annoying websites
        with open("settings/forbidden_websites.json", 'r') as f:
            self.forbidden_websites = json.load(f)["sites"]
        for i in range(len(self.forbidden_websites)):
            self.forbidden_websites[i] = decode_cesar(self.forbidden_websites[i], 10)
        separators = ["", "+", "-", "_", "/"]
        for site in self.forbidden_websites:
            if " " in site:
                for sep in separators:
                    self.forbidden_websites.append(site.replace(" ", sep))
        self.active_win_title, self.active_win_data = get_active_window()
        self.execute_task()

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        self.current_frame = page_name
        if page_name == "DailyPage":
            self.frames["DailyPage"].create_menu_bar()
        else:
            self.hide_menu()
        frame.tkraise()

    def hide_menu(self):
        menuBar = tk.Menu(self)
        self.config(menu = menuBar)

    def create_new_id(self, file_name):
        file_days = os.listdir("json_days")
        if file_name in file_days:
            with open("json_days/"+file_name, 'r') as f:
                day_tasks = json.load(f)
            day_tasks = day_tasks["tasks"]
            used_ids = list()
            for task in day_tasks:
                used_ids.append(int(task["infos"]["id"]))
            new_id = 0
            while new_id in used_ids:
                new_id+=1
        else:
            new_id = 0
        return new_id

    def save_task(self, title, content, category, date, repetition, allow_browser, streaks=0):
        allow_browser = bool(allow_browser)
        file_days = os.listdir("json_days")
        if date == "tomorrow":
            today = str(datetime.date.today() + datetime.timedelta(days=1))
        else:
            today = str(datetime.date.today())
        file_name = today+".json"
        file_path = "json_days/"+file_name
        new_id = self.create_new_id(file_name)
        new_task = {
            'infos': {
                'id': new_id,
                'title': encode_cesar(title, 10),
                'content': encode_cesar(content, 10),
                'category': encode_cesar(category, 10),
                'repetition': repetition,
                "allow_browser": allow_browser
            },
            'stats': {
                'done': False,
                'minutes': 0,
                'streaks': streaks
            }
        }
        if file_name in file_days:
            with open(file_path, 'r') as f:
                day_tasks = json.load(f)
            day_tasks["tasks"].append(new_task)
            data = day_tasks
        else:
            data = {
                'info': {
                    'date': today,
                    'fails': 0
                },
                'tasks': [new_task]
            }
        with open(file_path, 'w+') as outfile:
            json.dump(data, outfile, indent=4)
        # print("the new task was successfully created")

    def add_a_fail(self):
        file_days = os.listdir("json_days")
        file_name = str(datetime.date.today())+".json"
        file_path = "json_days/"+file_name
        if file_name in file_days:
            with open(file_path, 'r') as f:
                day_infos = json.load(f)
            if "fails" in day_infos["info"]:
                day_infos["info"]["fails"] = int(day_infos["info"]["fails"])+1
            else:
                day_infos["info"]["fails"] = 1
            data = day_infos
        else:
            data = {
                'info': {
                    'date': today,
                    'fails': 1
                },
                'tasks': list()
            }
        with open(file_path, 'w+') as outfile:
            json.dump(data, outfile, indent=4)

    def action_app_based(self, active_win_name, active_win_data, allow_browser, allow_forbidden):
        active_win_without_title = remove_substr_from_str(active_win_name, active_win_data)
        if active_win_name in ["Google Chrome", "Mozilla Firefox", "Microsoft​ Edge"]:
            if allow_browser:
                if not allow_forbidden:
                    for site in self.forbidden_websites:
                        if site in active_win_without_title.lower():
                            pyautogui.keyDown('ctrlleft')
                            pyautogui.press('w')
                            pyautogui.keyUp('ctrlleft')
                            self.add_a_fail()
            else:
                pyautogui.keyDown('ctrlleft')
                pyautogui.keyDown('shiftleft')
                pyautogui.press('w')
                pyautogui.keyUp('shiftleft')
                pyautogui.keyUp('ctrlleft')
                self.add_a_fail()


    def execute_task(self):
        if self.today != str(datetime.date.today()):
            self.frames["DailyPage"].transfer_tasks()
            self.frames["DailyPage"].reload_tasks()
            self.today = str(datetime.date.today())
        # if self.frames["TaskPage"].pom_status != "break":
        date_of_the_week = datetime.datetime.now().strftime("%A").lower()
        active_win_title, active_win_data = get_active_window()
        if (active_win_data != self.active_win_data) and (date_of_the_week not in ["saturday"]) and (self.current_frame != "BreakPage"):
            self.active_win_data = active_win_data
            self.action_app_based(active_win_title, active_win_data, self.frames["TaskPage"].allow_browser, False)
            # if self.current_frame != "BreakPage":
        self.after(2000, self.execute_task)


class DailyPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #left and right frames
        # self.columnconfigure(0, weight=1, minsize=100)
        self.columnconfigure(1, weight=10)
        self.rowconfigure(0, weight=1)
        self.frame_left = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_right = tk.Frame(self,relief=tk.SOLID,borderwidth=0)
        # self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew")

        #inside of frame left
        self.frame_left.columnconfigure(0, weight=1)
        self.frame_left.rowconfigure(0, weight=1)
        self.frame_left.rowconfigure(1, weight=1)
        self.frame_left.rowconfigure(2, weight=1)
        frame_left_coins = tk.Frame(self.frame_left,relief=tk.SOLID,borderwidth=2)
        frame_left_duration = tk.Frame(self.frame_left,relief=tk.SOLID,borderwidth=2)
        frame_left_streaks = tk.Frame(self.frame_left,relief=tk.SOLID,borderwidth=2)
        frame_left_coins.grid(row=0, column=0, sticky="nsew")
        frame_left_duration.grid(row=1, column=0, sticky="nsew")
        frame_left_streaks.grid(row=2, column=0, sticky="nsew")

        frame_left_coins.columnconfigure(0, weight=1)
        frame_left_coins.rowconfigure(0, weight=1)
        btn_stats = tk.Button(frame_left_coins, text="stats",
                        command=lambda: self.view_stats())
        btn_stats.grid(sticky="", row=0,column=0)

        frame_left_duration.columnconfigure(0, weight=1)
        frame_left_duration.rowconfigure(0, weight=1)
        btn_reload = tk.Button(frame_left_duration, text="reload",
                        command=lambda: self.reload_tasks())
        btn_reload.grid(sticky="", row=0,column=0)

        frame_left_streaks.columnconfigure(0, weight=1)
        frame_left_streaks.rowconfigure(0, weight=1)
        btn_break = tk.Button(frame_left_streaks, text="break",
                        command=lambda: self.take_break())
        btn_break.grid(sticky="", row=0,column=0)


        # data1 = {'Country': ['US','CA','GER','UK','FR'],
        #          'GDP_Per_Capita': [45000,42000,52000,49000,47000]
        #         }
        # df1 = DataFrame(data1,columns=['Country','GDP_Per_Capita'])
        # figure1 = plt.Figure(figsize=(1,1), dpi=100)
        # ax1 = figure1.add_subplot(111)
        # bar1 = FigureCanvasTkAgg(figure1, self.frame_left)
        # bar1.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        # df1 = df1[['Country','GDP_Per_Capita']].groupby('Country').sum()
        # df1.plot(kind='bar', legend=True, ax=ax1)
        # ax1.set_title('Country Vs. GDP Per Capita')

        #inside of frame right
        self.frame_right.columnconfigure(0, weight=1)
        self.frame_right.rowconfigure(0, weight=1)
        self.frame_right.rowconfigure(1, weight=8)
        # self.frame_right.rowconfigure(2, weight=1)
        frame_right_title = tk.Frame(self.frame_right,relief=tk.SOLID,borderwidth=0, bg="#ffffff")
        frame_right_add = tk.Frame(self.frame_right,relief=tk.SOLID,borderwidth=2)
        frame_right_title.grid(row=0, column=0, sticky="nsew")
        frame_right_add.grid(row=2, column=0, sticky="nsew")

        self.frame_right_tasks = tk.Frame(self.frame_right,relief=tk.SOLID,borderwidth=2)
        self.frame_right_tasks.grid(row=1, column=0, sticky="nsew")
        self.frame_right_tasks.rowconfigure(0, weight=1)
        self.frame_right_tasks.columnconfigure([0, 1], weight=1)

        self.frame_right_tasks_to_do = tk.Frame(self.frame_right_tasks,relief=tk.SOLID,borderwidth=2, bg="#FDCE2A", padx=10, pady=10)
        self.frame_right_tasks_done = tk.Frame(self.frame_right_tasks,relief=tk.SOLID,borderwidth=2, bg="#03C04A", padx=10, pady=10)
        self.frame_right_tasks_to_do.grid(row=0, column=0, sticky="nsew")
        self.frame_right_tasks_done.grid(row=0, column=1, sticky="nsew")
        self.frame_right_tasks_to_do.rowconfigure(0, weight=1)
        self.frame_right_tasks_to_do.rowconfigure(1, weight=10)
        self.frame_right_tasks_to_do.columnconfigure(0, weight=1)
        self.frame_right_tasks_done.rowconfigure(0, weight=1)
        self.frame_right_tasks_done.rowconfigure(1, weight=10)
        self.frame_right_tasks_done.columnconfigure(0, weight=1)

        #inside of frame_right_title
        frame_right_title.columnconfigure(0, weight=1)
        frame_right_title.rowconfigure(0, weight=1)
        self.date_string = tk.StringVar()
        self.date_string.set("test")
        label_title = tk.Label(frame_right_title, textvariable=self.date_string,
                                font=controller.normal_font, bg="#ffffff")
        label_title.grid(sticky="nsew")

        self.daily_tasks = get_daily_tasks()
        if len(self.daily_tasks) == 0:
            self.get_older_tasks()
        #inside of frame_right_tasks
        self.reload_tasks()

        # #inside of frame_right_add
        # frame_right_add.columnconfigure([0], weight=1)
        # frame_right_add.rowconfigure(0, weight=1)
        # string="Click to add a task [Ctrl+A]"
        # btn2 = tk.Button(frame_right_add, text=string, bg="grey",
        #                 command=self.show_addtask_page)
        # btn2.grid(sticky="", row=0,column=0)
        # # string="Click to take a break"
        # # btn3 = tk.Button(frame_right_add, text=string,
        # #                 command=lambda: controller.show_frame("BreakPage"))
        # # btn3.grid(sticky="nsew", row=0, column=0)

    def show_stats_time(self):
        self.controller.show_frame("StatsPage")
        self.controller.frames["StatsPage"].show_minutes()

    def show_stats_fails(self):
        self.controller.show_frame("StatsPage")
        self.controller.frames["StatsPage"].show_fails()

    def show_stats_habits(self):
        self.controller.show_frame("StatsPage")
        self.controller.frames["StatsPage"].show_habits()

    def create_menu_bar(self):
        menuBar = tk.Menu(self.controller)

        menu_task = tk.Menu(menuBar, tearoff=0)
        menu_task.add_command(label="Create Task", command=self.show_addtask_page)
        menu_task.add_command(label="Reload Tasks", command=self.reload_tasks)
        menuBar.add_cascade(label="Task", menu=menu_task)

        menu_stats = tk.Menu(menuBar, tearoff=0)
        menu_stats.add_command(label="Show time spent", command=self.show_stats_time)
        menu_stats.add_command(label="Show fails", command=self.show_stats_fails)
        menu_stats.add_command(label="Show successful habits", command=self.show_stats_habits)
        menuBar.add_cascade(label="Statistics", menu=menu_stats)

        menu_break = tk.Menu(menuBar, tearoff=0)
        menu_break.add_command(label="Take a break", command=self.take_break)
        menuBar.add_cascade(label="Break", menu=menu_break)

        # menuFile = tk.Menu(menuBar, tearoff=0)
        # menuFile.add_command(label="New", command=self.doSomething)
        # menuFile.add_command(label="Open", command=self.openFile)
        # menuFile.add_command(label="Save", command=self.doSomething)
        # menuFile.add_separator()
        # menuFile.add_command(label="Exit", command=self.quit)
        # menuBar.add_cascade( label="File", menu=menuFile)
        #
        # menuEdit = tk.Menu(menuBar, tearoff=0)
        # menuEdit.add_command(label="Undo", command=self.doSomething)
        # menuEdit.add_separator()
        # menuEdit.add_command(label="Copy", command=self.doSomething)
        # menuEdit.add_command(label="Cut", command=self.doSomething)
        # menuEdit.add_command(label="Paste", command=self.doSomething)
        # menuBar.add_cascade( label="Edit", menu=menuEdit)
        #
        # menuHelp = tk.Menu(menuBar, tearoff=0)
        # menuHelp.add_command(label="About", command=self.doAbout)
        # menuBar.add_cascade( label="Help", menu=menuHelp)

        self.controller.config(menu = menuBar)

    def show_addtask_page(self):
        self.controller.show_frame("AddTaskPage")
        self.controller.frames["AddTaskPage"].e1.focus()

    def reload_app(self):
        os.system("python main.py")

    def take_break(self):
        # showinfo("ShowInfo", "Hello World!")
        res = True
        i = 0
        while (i<5) and res:
            res = askokcancel("Break", "Do you really deserve a break ? ["+str(i)+"]")
            i+=1

        if res:
            self.controller.show_frame("BreakPage")

    def get_older_tasks(self):
        file_days = os.listdir("json_days")
        if len(file_days) > 0:
            file_name = file_days[-1]
            file_path = "json_days/"+file_name
            with open(file_path, 'r') as f:
                day_tasks = json.load(f)
            day_tasks = day_tasks["tasks"]
            for i in range(len(day_tasks)):
                task = day_tasks[i]
                if (not task["stats"]["done"]) or (task["infos"]["repetition"]):
                    if "allow_browser" in task["infos"]:
                        allow_browser = task["infos"]["allow_browser"]
                    else:
                        allow_browser = False
                    #test hier ou pas
                    if (task["stats"]["done"]) and (file_name.remove(".json") == str(datetime.date.today() - datetime.timedelta(days=1))):
                        streaks = task["stats"]["streaks"]
                    else:
                        streaks = 0
                    self.controller.save_task(decode_cesar(task["infos"]["title"], 10), decode_cesar(task["infos"]["content"], 10), decode_cesar(task["infos"]["category"], 10), "today", task["infos"]["repetition"], allow_browser, streaks)

    def transfer_tasks(self):
        for i in range(len(self.daily_tasks)):
            task = self.daily_tasks[i]
            if (not task["stats"]["done"]) or (task["infos"]["repetition"]):
                if "allow_browser" in task["infos"]:
                    allow_browser = task["infos"]["allow_browser"]
                else:
                    allow_browser = False
                if task["stats"]["done"]:
                    streaks = task["stats"]["streaks"]
                else:
                    streaks = 0
                self.controller.save_task(decode_cesar(task["infos"]["title"], 10), decode_cesar(task["infos"]["content"], 10), decode_cesar(task["infos"]["category"], 10), "today", task["infos"]["repetition"], allow_browser, streaks)

    def destroy_previous_scroll(self):
        children = self.frame_right_tasks_to_do.winfo_children()
        for wid in children:
            wid.destroy()
        children = self.frame_right_tasks_done.winfo_children()
        for wid in children:
            wid.destroy()

    def alphabetically_order_cat(self, cats):
        cats_names = cats.keys()
        cats_names_decoded = list()
        for cat_name in cats_names:
            cats_names_decoded.append(decode_cesar(cat_name, 10))
        cats_names_decoded = sorted(cats_names_decoded)
        sorted_cats = dict()
        for sorted_cat_name in cats_names_decoded:
            for cat_name in cats:
                if decode_cesar(cat_name, 10) == sorted_cat_name:
                    sorted_cats[encode_cesar(sorted_cat_name, 10)] = cats[cat_name]
        return sorted_cats

    def reload_tasks(self):
        full_date = ""+datetime.datetime.now().strftime("%A %d %B %Y")
        self.date_string.set(full_date)
        self.destroy_previous_scroll()
        #sep
        label_cat = tk.Label(self.frame_right_tasks_to_do, text="TO DO", font=self.controller.subtitle_font, bg="#FDCE2A")
        label_cat.grid(row=0, column=0, sticky="nsew")
        label_cat2 = tk.Label(self.frame_right_tasks_done, text="DONE", font=self.controller.subtitle_font, bg="#03C04A")
        label_cat2.grid(row=0, column=0, sticky="nsew")
        self.daily_tasks = get_daily_tasks()
        self.daily_tasks.reverse()
        if len(self.daily_tasks) == 0:
            label_task = tk.Label(self.frame_right_tasks_to_do, text="no tasks for today")
            label_task.grid(row=0, column=0, sticky="nsew")
        else:
            self.scroll_tasks_done = ScrollableFrame(self.frame_right_tasks_done, bg1="#03C04A")
            self.scroll_tasks_done.grid(row=1, column=0, sticky="nsew")
            self.scroll_tasks_to_do = ScrollableFrame(self.frame_right_tasks_to_do, bg1="#FDCE2A")
            self.scroll_tasks_to_do.grid(row=1, column=0, sticky="nsew")
            tasks_by_categories = {
                "to_do": dict(),
                "done": dict()
            }

            for i in range(len(self.daily_tasks)):
                cat = self.daily_tasks[i]["infos"]["category"]
                if self.daily_tasks[i]["stats"]["done"]:
                    if not cat in tasks_by_categories["done"]:
                        tasks_by_categories["done"][cat] = list()
                    tasks_by_categories["done"][cat].append(self.daily_tasks[i])
                else:
                    if not cat in tasks_by_categories["to_do"]:
                        tasks_by_categories["to_do"][cat] = list()
                    tasks_by_categories["to_do"][cat].append(self.daily_tasks[i])

            # tasks_by_categories["to_do"] = sorted(tasks_by_categories["to_do"].keys(), key=lambda x:x.lower())
            tasks_by_categories["to_do"] = self.alphabetically_order_cat(tasks_by_categories["to_do"])
            tasks_by_categories["done"] = self.alphabetically_order_cat(tasks_by_categories["done"])
            # tasks_by_categories["done"] = sorted(tasks_by_categories["done"].keys(), key=lambda x:x.lower())
            for cat in tasks_by_categories["to_do"]:
                frame_sep = tk.Frame(self.scroll_tasks_to_do.scrollable_frame,
                                        relief=tk.SOLID, borderwidth=1, bg="#DDDDDD",
                                        padx=5, pady=10)
                frame_sep.grid(sticky="nsw")
                frame_sep.columnconfigure(0, weight=1)
                frame_sep.rowconfigure(0, weight=1)
                string = cat.capitalize()
                label_cat = tk.Label(frame_sep, text=decode_cesar(string, 10), font=self.controller.category_font,bg="#DDDDDD", pady="10")
                label_cat.grid(row=0, column=0, sticky="nsew")
                for i in range(len(tasks_by_categories["to_do"][cat])):
                    t = tasks_by_categories["to_do"][cat][i]
                    frame_task = tk.Frame(self.scroll_tasks_to_do.scrollable_frame,
                                            relief=tk.SOLID,borderwidth=1,
                                            bg="#FFFFFF",
                                            padx=20, pady=10)
                    frame_task.grid(sticky="nsew")
                    frame_task.rowconfigure(0, weight=1)
                    if t["infos"]["repetition"]:
                        offset = 1
                        frame_task.columnconfigure(0, weight=1)
                        frame_task.columnconfigure(1, weight=3)
                        frame_task.columnconfigure(2, weight=1)
                        string = "Daily ["+str(t["stats"]["streaks"])+"]"
                        label_daily = tk.Label(frame_task, text=string, font=self.controller.daily_category_font, fg="#FF0000")
                        label_daily.grid(row=0, column=0, sticky="nsw")
                    else:
                        offset = 0
                        frame_task.columnconfigure(0, weight=3)
                        frame_task.columnconfigure(1, weight=1)
                    substr = ""
                    btn_text = "start"
                    if int(t["stats"]["minutes"]) > 0:
                        time_spent = readable_times(0, int(t["stats"]["minutes"]), 0)
                        substr+=" ("+time_spent+")"
                        btn_text = "pursue"
                    string = decode_cesar(t["infos"]["title"], 10).upper()+substr
                    label_task = tk.Label(frame_task, text=string, bg="#FFFFFF")
                    label_task.grid(row=0, column=0+offset, sticky="nsw")
                    btn_task= tk.Button(frame_task, text=btn_text,
                                        command=lambda t=t: self.view_task(t),
                                        bg="#FDCE2A")
                    btn_task.grid(row=0, column=1+offset, sticky="nse")

                label_empty = tk.Label(self.scroll_tasks_to_do.scrollable_frame, text="", bg="#FDCE2A")
                label_empty.grid(sticky="we")


            for cat in tasks_by_categories["done"]:
                frame_sep = tk.Frame(self.scroll_tasks_done.scrollable_frame,
                                        relief=tk.SOLID,borderwidth=1, bg="#DDDDDD",
                                        padx=5, pady=10)
                frame_sep.grid(sticky="nsw")
                frame_sep.columnconfigure(0, weight=1)
                frame_sep.rowconfigure(0, weight=1)
                string = cat.capitalize()
                label_cat = tk.Label(frame_sep, text=decode_cesar(string, 10), font=self.controller.category_font,bg="#DDDDDD", pady="10")
                label_cat.grid(row=0, column=0, sticky="nsew")
                for i in range(len(tasks_by_categories["done"][cat])):
                    t = tasks_by_categories["done"][cat][i]
                    frame_task = tk.Frame(self.scroll_tasks_done.scrollable_frame,
                                            relief=tk.SOLID,borderwidth=1,
                                            bg="#FFFFFF",
                                            padx=20, pady=10)
                    frame_task.grid(sticky="nsew")
                    frame_task.rowconfigure(0, weight=1)
                    if t["infos"]["repetition"]:
                        offset = 1
                        frame_task.columnconfigure(0, weight=1)
                        frame_task.columnconfigure(1, weight=3)
                        frame_task.columnconfigure(2, weight=1)
                        string = "Daily ["+str(t["stats"]["streaks"])+"]"
                        label_daily = tk.Label(frame_task, text=string, font=self.controller.daily_category_font, fg="#FF0000")
                        label_daily.grid(row=0, column=0, sticky="nsw")
                    else:
                        offset = 0
                        frame_task.columnconfigure(0, weight=3)
                        frame_task.columnconfigure(1, weight=1)
                    substr = ""
                    btn_text = "start"
                    if int(t["stats"]["minutes"]) > 0:
                        time_spent = readable_times(0, int(t["stats"]["minutes"]), 0)
                        substr+=" ("+time_spent+")"
                        btn_text = "pursue"
                    string = decode_cesar(t["infos"]["title"], 10).upper()+substr
                    label_task = tk.Label(frame_task, text=string, bg="#FFFFFF")
                    label_task.grid(row=0, column=0+offset, sticky="nsw")
                    # label_done = tk.Label(frame_task, text="done!", fg="black", bg="#03C04A")
                    # label_done.grid(row=0, column=1, sticky="nse")
                label_empty = tk.Label(self.scroll_tasks_done.scrollable_frame, text="", bg="#03C04A")
                label_empty.grid(sticky="we")


    def view_task(self, task):
        self.controller.show_frame("TaskPage")
        self.controller.frames["TaskPage"].create_title(task)

    def view_stats(self):
        self.controller.show_frame("StatsPage")
        self.controller.frames["StatsPage"].show_minutes()


class TaskPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.pom_status = "work"
        self.allow_browser = True

        #left and right frames
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=6)
        self.rowconfigure(2, weight=1)
        self.frame_title = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_center = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_bottom = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_title.grid(row=0, column=0, sticky="nsew")
        self.frame_center.grid(row=1, column=0, sticky="nsew")
        self.frame_bottom.grid(row=2, column=0, sticky="nsew")

        #inside frame_title
        self.frame_title.rowconfigure(0, weight=1)
        self.frame_title.rowconfigure(1, weight=1)
        self.frame_title.columnconfigure(0, weight=1)

        #inside frame_center
        self.frame_center.rowconfigure(0, weight=1)
        self.frame_center.columnconfigure(0, weight=1)
        self.frame_center.columnconfigure(1, weight=1)

        self.frame_c_left = tk.Frame(self.frame_center,relief=tk.SOLID,borderwidth=2)
        self.frame_c_right = tk.Frame(self.frame_center,relief=tk.SOLID,borderwidth=2, bg="#FFFFFF")
        self.frame_c_left.grid(row=0, column=0,sticky="nsew")
        self.frame_c_right.grid(row=0, column=1,sticky="nsew")
        self.frame_c_left.rowconfigure([0,1], weight=1)
        self.frame_c_left.columnconfigure(0, weight=1)
        self.frame_c_right.rowconfigure([0,3], weight=1)
        self.frame_c_right.columnconfigure(0, weight=1)

        string = "total time spent today: "
        center_label = tk.Label(self.frame_c_left, text=string, font=self.controller.duration_font)
        center_label.grid(row=0, column=0,sticky="nsew")
        # citation = "“Ce que je cherche avant tout, c’est la grandeur :\nce qui est grand est toujours beau.”\n N"
        # citation_label = tk.Label(self.frame_center, text=citation, font=self.controller.citation_font)
        # citation_label.grid(row=0, column=0,sticky="nsew")
        self.duration_string = tk.StringVar()
        self.duration_string.set("0")
        self.duration_label = tk.Label(self.frame_c_left, textvariable=self.duration_string, font=self.controller.duration_font)
        self.duration_label.grid(row=1, column=0,sticky="nsew")

        string = "Pomodoro"
        pom_label = tk.Label(self.frame_c_right, text=string, font=self.controller.title_font)
        pom_label.grid(row=0, column=0)
        self.pom_btn_string = tk.StringVar()
        self.pom_btn_col = tk.StringVar()
        self.pom_btn_string.set("click to start")
        self.btn_pom = tk.Button(self.frame_c_right, textvariable=self.pom_btn_string, bg="#03C04A",
                           command=lambda: self.pom_action())
        self.btn_pom.grid(row=1, column=0)
        self.status_pom_string = tk.StringVar()
        self.status_pom_string.set("")
        self.status_pom_label = tk.Label(self.frame_c_right, textvariable=self.status_pom_string, font=self.controller.duration_font)
        self.status_pom_label.grid(row=2, column=0)
        self.duration_pom_string = tk.StringVar()
        self.duration_pom_string.set("")
        self.duration_pom_label = tk.Label(self.frame_c_right, textvariable=self.duration_pom_string, font=self.controller.duration_font)
        self.duration_pom_label.grid(row=3, column=0)

        #inside frame_bottom
        self.frame_bottom.rowconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(2, weight=1)

        btn_exit = tk.Button(self.frame_bottom, text="continuer plus tard", bg="#FDCE2A",
                           command=lambda: self.go_back())
        btn_exit.grid(row=0, column=0)
        btn_done = tk.Button(self.frame_bottom, text="Task is done", bg="#03C04A",
                           command=lambda: self.mark_task_done())
        btn_done.grid(row=0, column=2)

    def pom_action(self):
        self.pom_status = "work"
        if self.pom_btn_string.get() == "click to start":
            self.pom_btn_string.set("click to end")
            self.btn_pom.configure(bg="#FFFFFF")
            self.status_pom_string.set(self.pom_status.upper())
            self.pom_time_begin = time.time()
            self.pom_duration = 60*25 - 1
            self.frame_c_right.configure(bg="#03C04A")
            self.pomodoro()
        else:
            self.pom_btn_string.set("click to start")
            self.btn_pom.configure(bg="#03C04A")
            self.status_pom_string.set("")
            self.duration_pom_string.set("")
            self.frame_c_right.configure(bg="#FFFFFF")

    def pomodoro(self):
        t_left = int((self.pom_time_begin + self.pom_duration) - time.time())
        minutes = t_left//60
        seconds = t_left-minutes*60
        string = "left: "+two_digits_number(minutes)+":"+two_digits_number(seconds)
        self.duration_pom_string.set(string)
        if t_left <= 0:
            self.pom_time_begin = time.time()
            if self.pom_status == "work":
                self.frame_c_right.configure(bg="#FDCE2A")
                pygame.mixer.music.load("404359__kagateni__success2.wav")
                pygame.mixer.music.play()
                self.pom_status = "break"
                self.pom_duration = 60*5
            else:
                self.frame_c_right.configure(bg="#03C04A")
                pygame.mixer.music.load("404359__kagateni__success2.wav")
                pygame.mixer.music.play()
                self.pom_status = "work"
                self.pom_duration = 60*25
        if (self.pom_btn_string.get() != "click to start") and (self.controller.current_frame == "TaskPage"):
            self.controller.after(1000, self.pomodoro)
        else:
            self.duration_pom_string.set("")


    def go_back(self):
        self.update_time_spent_task()
        self.controller.show_frame("DailyPage")

    def go_tack_break(self):
        if int(time.time() - self.begin_time) >= 0:
            self.controller.show_frame("BreakPage")

    def update_time_spent_task(self):
        duration = int(time.time() - self.begin_time)
        minutes = duration//60
        file_days = os.listdir("json_days")
        today = str(datetime.date.today())
        file_name = today+".json"
        file_path = "json_days/"+file_name
        try:
            with open(file_path, 'r') as f:
                day_tasks = json.load(f)
            for task in day_tasks["tasks"]:
                if task["infos"]["id"] == self.task_id:
                    task["stats"]["minutes"] = int(task["stats"]["minutes"])+minutes
            with open(file_path, 'w+') as outfile:
                json.dump(day_tasks, outfile, indent=4)
        except Exception as e:
            print("yesterday")
        self.allow_browser = True
        self.controller.frames["DailyPage"].reload_tasks()

    def create_title(self, task):
        self.begin_time = time.time()
        self.task = task
        self.task_id = task["infos"]["id"]
        string = decode_cesar(task["infos"]["category"]+" : "+task["infos"]["title"],10)
        if task["infos"]["repetition"]:
            string += " (daily)"
        self.title = tk.Label(self.frame_title, text=string.upper(), font=self.controller.title_font)
        self.title.grid(row=0, column=0,sticky="nsew")
        self.content = tk.Label(self.frame_title, text=task["infos"]["content"])
        self.content.grid(row=1, column=0,sticky="nsew")
        self.update_duration()
        self.pom_btn_string.set("click to start")
        self.btn_pom.configure(bg="#03C04A")
        self.frame_c_right.configure(bg="#FFFFFF")
        self.status_pom_string.set("")
        self.duration_pom_string.set("")
        btn_end = tk.Button(self.frame_bottom, text="stop daily repetition/delete", command=lambda: self.remove_task())
        btn_end.grid(row=0, column=1)
        if "allow_browser" in task["infos"]:
            self.allow_browser = task["infos"]["allow_browser"]
        else:
            self.allow_browser = False

    def remove_task(self):
        file_days = os.listdir("json_days")
        file_name = str(datetime.date.today())+".json"
        file_path = "json_days/"+file_name
        if file_name in file_days:
            with open(file_path, 'r') as f:
                day_tasks = json.load(f)
            day_tasks_without = dict(day_tasks)
            day_tasks_without["tasks"] = list()
            for task in day_tasks["tasks"]:
                if task["infos"]["id"] != self.task_id:
                    day_tasks_without["tasks"].append(task)
            with open(file_path, 'w+') as outfile:
                json.dump(day_tasks_without, outfile, indent=4)
        self.update_time_spent_task()
        self.controller.show_frame("DailyPage")

    def update_duration(self):
        duration = int(time.time() - self.begin_time)
        hours = duration//3600
        minutes = (duration-hours*3600)//60
        seconds = duration-hours*3600-minutes*60
        hours_stored = int(self.task["stats"]["minutes"])//60
        minutes_stored = int(self.task["stats"]["minutes"]) - hours_stored*60
        minutes_corrected = (minutes + minutes_stored)%60
        hours_corrected = hours_stored + hours + (minutes + minutes_stored)//60
        string = two_digits_number(hours_corrected)+":"+two_digits_number(minutes_corrected)+":"+two_digits_number(seconds)
        self.duration_string.set(string)
        if self.controller.current_frame == "TaskPage":
            self.controller.after(1000, self.update_duration)
        else:
            self.duration_string.set("0")

    def mark_task_done(self):
        pygame.mixer.music.load("404358__kagateni__success-[AudioTrimmer.com].wav")
        pygame.mixer.music.play()
        file_days = os.listdir("json_days")
        today = str(datetime.date.today())
        file_name = today+".json"
        file_path = "json_days/"+file_name
        try:
            with open(file_path, 'r') as f:
                day_tasks = json.load(f)
            for task in day_tasks["tasks"]:
                if task["infos"]["id"] == self.task_id:
                    task["stats"]["done"] = True
                    if task["infos"]["repetition"]:
                        task["stats"]["streaks"] = int(task["stats"]["streaks"]) + 1
            with open(file_path, 'w+') as outfile:
                json.dump(day_tasks, outfile, indent=4)
        except Exception as e:
            print("yesterday")
        self.update_time_spent_task()
        self.controller.show_frame("DailyPage")
        # pygame.mixer.music.load("404359__kagateni__success2.wav")
        # self.controller.after(1000, lambda: pygame.mixer.music.play())


class BreakPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #left and right frames
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1, minsize=50)
        self.rowconfigure(1, weight=6, minsize=50)
        self.rowconfigure(2, weight=1, minsize=50)
        self.frame_title = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_center = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_bottom = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_title.grid(row=0, column=0, sticky="nsew")
        self.frame_center.grid(row=1, column=0, sticky="nsew")
        self.frame_bottom.grid(row=2, column=0, sticky="nsew")

        #inside frame_bottom
        self.frame_bottom.rowconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(2, weight=1)

        btn_exit = tk.Button(self.frame_bottom, text="Go back", bg="#C23B22",
                           command=lambda: self.go_back())
        btn_exit.grid(row=0, column=0)

    def go_back(self):
        self.controller.show_frame("DailyPage")
        self.controller.execute_task()


class StatsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1, minsize=50)
        self.rowconfigure(1, weight=6, minsize=50)
        self.rowconfigure(2, weight=1, minsize=50)
        self.frame_title = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_center = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_bottom = tk.Frame(self,relief=tk.SOLID,borderwidth=2)
        self.frame_title.grid(row=0, column=0, sticky="nsew")
        self.frame_center.grid(row=1, column=0, sticky="nsew")
        self.frame_bottom.grid(row=2, column=0, sticky="nsew")

        #inside frame_title
        self.frame_title.rowconfigure(0, weight=1)
        self.frame_title.columnconfigure(0, weight=1)
        self.title = tk.Label(self.frame_title, text="stats of the week".upper(), font=self.controller.title_font)
        self.title.grid(row=0, column=0,sticky="nsew")

        #inside frame_center
        self.frame_center.rowconfigure(0, weight=1)
        self.frame_center.columnconfigure(0, weight=1)

        #inside frame_bottom
        self.frame_bottom.rowconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(2, weight=1)
        self.frame_bottom.columnconfigure(3, weight=1)

        btn_exit = tk.Button(self.frame_bottom, text="Go back", bg="#C23B22",
                           command=lambda: self.go_back())
        btn_exit.grid(row=0, column=0)
        btn_minutes = tk.Button(self.frame_bottom, text="stats minutes",
                           command=lambda: self.show_minutes())
        btn_minutes.grid(row=0, column=1)
        btn_fails = tk.Button(self.frame_bottom, text="stats fails",
                           command=lambda: self.show_fails())
        btn_fails.grid(row=0, column=2)
        btn_habits = tk.Button(self.frame_bottom, text="stats habits",
                           command=lambda: self.show_habits())
        btn_habits.grid(row=0, column=3)

    def show_habits(self):
        task_habits_title = list()
        task_habits_days = list()
        file_days = os.listdir("json_days")
        day = datetime.date.today()
        file_name = str(day)+".json"
        file_path = "json_days/"+file_name
        with open(file_path, 'r') as f:
            day_tasks = json.load(f)
        # i = -1
        for t in day_tasks["tasks"]:
            if "repetition" in t["infos"]:
                if t["infos"]["repetition"]:
                    # i += 1
                    task_habits_title.append(decode_cesar(t["infos"]["title"], 10))
                    task_habits_days.append(t["stats"]["streaks"])
                    # if t["stats"]["done"]:
                    #     task_habits_days[i]+=1
                    # still_running = True
                    # j = 0
                    # while still_running:
                    #     still_running = False
                    #     j += 1
                    #     file_days = os.listdir("json_days")
                    #     day = datetime.date.today() - datetime.timedelta(days=j)
                    #     file_name = str(day)+".json"
                    #     file_path = "json_days/"+file_name
                    #     with open(file_path, 'r') as f:
                    #         day_tasks2 = json.load(f)
                    #     for t2 in day_tasks2["tasks"]:
                    #         if "repetition" in t["infos"]:
                    #             if (t2["infos"]["title"] == task_habits_title[i]) and t2["infos"]["repetition"] and t2["stats"]["done"]:
                    #                 task_habits_days[i] += 1
                    #                 still_running = True
        # print(task_habits_title)
        # print(task_habits_days)
        data1 = {
            'tasks': task_habits_title,
            'cards': task_habits_days
        }
        try:
            self.bar1.get_tk_widget().destroy()
        except Exception as e:
            pass
        df1 = DataFrame(data1,columns=['tasks','cards'])
        figure1 = plt.Figure(figsize=(1,1), dpi=100)
        ax1 = figure1.add_subplot(111)
        self.bar1 = FigureCanvasTkAgg(figure1, self.frame_center)
        self.bar1.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        df1 = df1[['tasks','cards']].groupby('tasks').sum()
        df1.plot(kind='bar', legend=True, ax=ax1)
        ax1.set_title('days of successful habits')


    def show_fails(self):
        week_dates = list()
        day_fails = list()
        for i in range(15):
            file_days = os.listdir("json_days")
            day = datetime.date.today() - datetime.timedelta(days=i)
            file_name = str(day)+".json"
            file_path = "json_days/"+file_name
            week_dates.append(str(day)+"_"+day.strftime("%a"))
            day_fails.append(0)
            try:
                with open(file_path, 'r') as f:
                    day_tasks = json.load(f)
                if "fails" in day_tasks["info"]:
                    day_fails[i] += int(day_tasks["info"]["fails"])
            except Exception as e:
                pass
        data1 = {
            'dates': week_dates,
            'fails': day_fails
        }
        try:
            self.bar1.get_tk_widget().destroy()
        except Exception as e:
            pass
        df1 = DataFrame(data1,columns=['dates','fails'])
        figure1 = plt.Figure(figsize=(1,1), dpi=100)
        ax1 = figure1.add_subplot(111)
        self.bar1 = FigureCanvasTkAgg(figure1, self.frame_center)
        self.bar1.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        df1 = df1[['dates','fails']].groupby('dates').sum()
        df1.plot(kind='bar', legend=True, ax=ax1)
        ax1.set_title('daily fails of the last 15 days')

    def show_minutes(self):
        week_dates = list()
        day_work_times = list()
        for i in range(15):
            file_days = os.listdir("json_days")
            day = datetime.date.today() - datetime.timedelta(days=i)
            file_name = str(day)+".json"
            file_path = "json_days/"+file_name
            week_dates.append(str(day)+"_"+day.strftime("%a"))
            day_work_times.append(0)
            try:
                with open(file_path, 'r') as f:
                    day_tasks = json.load(f)
                for task in day_tasks["tasks"]:
                    if "minutes" in task["stats"]:
                        day_work_times[i] += int(task["stats"]["minutes"])
            except Exception as e:
                pass

        # data1 = {'Country': ['US','CA','GER','UK','FR'],
        #          'GDP_Per_Capita': [45000,42000,52000,29000,47000]
        #         }
        data1 = {
            'dates': week_dates,
            'worked_minutes': day_work_times
        }
        try:
            self.bar1.get_tk_widget().destroy()
        except Exception as e:
            pass
        df1 = DataFrame(data1,columns=['dates','worked_minutes'])
        figure1 = plt.Figure(figsize=(1,1), dpi=100)
        ax1 = figure1.add_subplot(111)
        self.bar1 = FigureCanvasTkAgg(figure1, self.frame_center)
        self.bar1.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        df1 = df1[['dates','worked_minutes']].groupby('dates').sum()
        df1.plot(kind='bar', legend=True, ax=ax1)
        # df1.tight_layout()
        ax1.set_title('Worked minutes of the last 15 days')

    def go_back(self):
        self.controller.show_frame("DailyPage")
        self.controller.execute_task()


class AddTaskPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.rowconfigure([0,8], weight=1)
        self.columnconfigure([0,1], weight=1)
        label = tk.Label(self, text="Create a task", font=controller.title_font)
        label.grid(row=0, column=0, pady=10)
        tk.Label(self, text="title").grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="content").grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="sub tasks (use '/')").grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="category").grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="date").grid(row=5, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="repetition").grid(row=6, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(self, text="allow browser").grid(row=7, column=0, sticky="nsew", padx=10, pady=10)
        self.e1 = tk.Entry(self)
        self.e2 = tk.Entry(self)
        self.e7 = tk.Entry(self)
        # self.e3 = tk.Entry(self)
        # self.e4 = tk.Entry(self)
        # self.e4.insert(tk.END, "today")
        self.e1.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.e2.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        self.e7.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        # self.e3.grid(row=3, column=1)
        #drop
        OPTIONS = [
            "today",
            "tomorrow"
        ]
        self.e4 = tk.StringVar()
        self.e4.set(OPTIONS[0])
        w = tk.OptionMenu(self, self.e4, *OPTIONS)
        w.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)
        #drop
        CATEGORIES = [
            "mathématiques",
            "physique-chimie",
            "science de l'ingénieur",
            "informatique pour tous",
            "tipe",
            "anglais",
            "français-philo",
            "sport",
            "programmation",
            "loisirs",
            "autres"
        ]
        self.e3 = tk.StringVar()
        self.e3.set(CATEGORIES[0])
        w2 = tk.OptionMenu(self, self.e3, *CATEGORIES)
        w2.grid(row=4, column=1, sticky="nsew", padx=10, pady=10)
        #
        #allow
        self.e6 = tk.IntVar()
        w3 = tk.Checkbutton(self, variable=self.e6)
        w3.grid(row=7, column=1, sticky="nsew", padx=10, pady=10)
        #
        #drop
        TYPES = [
            "only one time",
            "daily"
        ]
        self.e5 = tk.StringVar()
        self.e5.set(TYPES[0])
        w3 = tk.OptionMenu(self, self.e5, *TYPES)
        w3.grid(row=6, column=1, sticky="nsew", padx=10, pady=10)
        #
        button = tk.Button(self, text="Go back",
                           command=lambda: controller.show_frame("DailyPage"))
        button.grid(row=8, column=0)
        button_save = tk.Button(self, text="Save",
                           command=lambda: self.save_new_task(self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get(), self.e5.get(), self.e7.get(), self.e6.get()))
        button_save.grid(row=8, column=1)

    def save_new_task(self, title, content, category, date, repetition, subtasks, allow_browser):
        if (title != ""):
            subtasks = subtasks.split("/")
            if repetition == "daily":
                repetition = True
            else:
                repetition = False
            if subtasks != ['']:
                for i in range(len(subtasks)):
                    t = title+" ["+subtasks[i]+"]"
                    self.controller.save_task(t, content, category, date, repetition, allow_browser)
            else:
                self.controller.save_task(title, content, category, date, repetition, allow_browser)
            self.e1.delete(0, tk.END)
            self.e2.delete(0, tk.END)
            self.e7.delete(0, tk.END)
            self.e6.set(0)
            self.e4.set("today")
            self.e3.set("mathématiques")
            self.e5.set("only one time")
            self.controller.show_frame("DailyPage")
            self.controller.frames["DailyPage"].reload_tasks()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
