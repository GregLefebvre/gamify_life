# from pprint import pprint
# from win32gui import GetWindowText, GetForegroundWindow
# import time
# import pyautogui
# from win10toast import ToastNotifier
#
# def send_toast(str, substr=""):
#     toaster = ToastNotifier()
#     toaster.show_toast(str, substr, icon_path=None, duration=1, threaded=True)
#
# def get_active_window():
#     active_win = GetWindowText(GetForegroundWindow())
#     active_win_data = active_win
#     applications = ["Google Chrome", "Adobe Acrobat Reader DC", "console", "Discord", "Command Prompt",
#                     "Mail", "Calendar", "Mozilla Firefox", "Microsoft​ Edge"]
#     for app in applications:
#         if app in active_win:
#             active_win_data = app
#     if active_win_data == "console":
#         active_win_data = "Command Prompt"
#     elif active_win_data == "C:":
#         active_win_data = "File explorer"
#     return active_win_data, active_win
#
# def remove_substr_from_str(substr, str):
#     res = str
#     if substr in str:
#         for i in range(len(str)):
#             if str[i:i+len(substr)] == substr:
#                 res = str[:i]+str[min(i+len(substr), len(str)):]
#     return res
#
# def action_app_based(active_win_name, active_win_data):
#     restricted_websites = ["instagram", "twitter", "jeuxvideo"]
#     active_win_without_title = remove_substr_from_str(active_win_name, active_win_data)
#     if active_win_name in ["Google Chrome", "Mozilla Firefox", "Microsoft​ Edge"]:
#         for site in restricted_websites:
#             if site in active_win_without_title.lower():
#                 pyautogui.keyDown('ctrlleft')
#                 pyautogui.press('w')
#                 pyautogui.keyUp('ctrlleft')
#                 send_toast("THIS WEBSITE AIN'T GOOD FOR YOU!","!!!")
#                 print("- - -")
#                 print("closed: "+active_win_without_title)
#                 print("- - -")
#
#
# _, active_win_data = get_active_window()
# print(active_win_data)
# while 1:
#     act, data = get_active_window()
#     if active_win_data != data:
#         active_win_data = data
#         print(active_win_data)
#         action_app_based(act, data)
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import sys

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.createWidgets()

    def createWidgets(self):
        fig=plt.figure(figsize=(8,8))
        ax=fig.add_axes([0.1,0.1,0.8,0.8],polar=True)
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)
        canvas.show()

        self.plotbutton=tk.Button(master=root, text="plot", command=lambda: self.plot(canvas,ax))
        self.plotbutton.grid(row=0,column=0)

    def plot(self,canvas,ax):
        c = ['r','b','g']  # plot marker colors
        ax.clear()         # clear axes from previous plot
        for i in range(3):
            theta = np.random.uniform(0,360,10)
            r = np.random.uniform(0,1,10)
            ax.plot(theta,r,linestyle="None",marker='o', color=c[i])
            canvas.draw()

root=tk.Tk()
app=Application(master=root)
app.mainloop()
