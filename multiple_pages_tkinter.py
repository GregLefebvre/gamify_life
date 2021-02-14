import tkinter as tk                # python 3
from tkinter import font as tkfont # python 3
import pyautogui, datetime
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.rowconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=200)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize_frame)
        scrollbar.pack(side="right", fill="y")

    def resize_frame(self, e):
        self.canvas.itemconfig(self.win, width=self.canvas.winfo_width()-2)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/100)), "units")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Arial', size=18, weight="bold", slant="italic")

        l = str(int(pyautogui.size()[1]*0.75))
        self.geometry(l+'x'+l)
        self.title("Gamify your life")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be GROOVE above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DailyPage, TaskPage, AddTaskPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DailyPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class DailyPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #left and right frames
        self.columnconfigure(0, weight=1, minsize=100)
        self.columnconfigure(1, weight=4, minsize=400)
        self.rowconfigure(0, weight=1, minsize=50)
        frame_left = tk.Frame(self,relief=tk.GROOVE,borderwidth=2)
        frame_right = tk.Frame(self,relief=tk.GROOVE,borderwidth=2)
        frame_left.grid(row=0, column=0, sticky="nsew")
        frame_right.grid(row=0, column=1, sticky="nsew")

        #inside of frame right
        frame_right.columnconfigure(0, weight=1)
        frame_right.rowconfigure(0, weight=1, minsize=0)
        frame_right.rowconfigure(1, weight=6, minsize=0)
        frame_right.rowconfigure(2, weight=1, minsize=0)
        frame_right_title = tk.Frame(frame_right,relief=tk.GROOVE,borderwidth=2)
        frame_right_add = tk.Frame(frame_right,relief=tk.GROOVE,borderwidth=2)
        frame_right_tasks = ScrollableFrame(frame_right)
        frame_right_title.grid(row=0, column=0, sticky="nsew")
        frame_right_add.grid(row=2, column=0, sticky="nsew")
        frame_right_tasks.grid(row=1, column=0, sticky="nsew")

        #inside of frame_right_title
        frame_right_title.columnconfigure(0, weight=1)
        frame_right_title.rowconfigure(0, weight=1)
        string = "Today is "+str(datetime.date.today())
        label_title = tk.Label(frame_right_title, text=string,
                                font=controller.title_font,
                                borderwidth=2,
                                relief=tk.GROOVE)
        label_title.grid(sticky="nsew")

        #inside of frame_right_tasks
        nb = 25
        for i in range(nb):
            frame_task = tk.Frame(frame_right_tasks.scrollable_frame,
                                    relief=tk.SOLID,borderwidth=2,
                                    padx=20, pady=20)
            frame_task.grid(sticky="nsew")
            frame_task.columnconfigure(0, weight=3)
            frame_task.columnconfigure(1, weight=1)
            frame_task.rowconfigure(0, weight=1)
            string = "Task "+str(i)
            label_task = tk.Label(frame_task, text=string)
            label_task.grid(row=0, column=0, sticky="nsew")
            btn_task= tk.Button(frame_task, text="view",
                                command=lambda: controller.show_frame("TaskPage"))
            btn_task.grid(row=0, column=1, sticky="nsew")


        #inside of frame_right_add
        frame_right_add.columnconfigure(0, weight=1)
        frame_right_add.rowconfigure(0, weight=1)
        string="Click to add a task"
        btn2 = tk.Button(frame_right_add, text=string,
                        command=lambda: controller.show_frame("AddTaskPage"))
        btn2.grid(sticky="nsew")

        # btn3 = tk.Button(frame_right_tasks, text="3")
        # btn3.pack(padx=5, pady=5)




        # for i in range(3):
        #     window.columnconfigure(i, weight=1, minsize=75)
        #     window.rowconfigure(i, weight=1, minsize=50)
        #
        #     for j in range(0, 3):
        #         frame = tk.Frame(
        #             master=window,
        #             relief=tk.GROOVE,
        #             borderwidth=2
        #         )
        #         frame.grid(row=i, column=j, padx=5, pady=5)
        #
        #         btn = tk.Button(master=frame, text=f"Row {i}\nColumn {j}")
        #         btn.pack(padx=5, pady=5)








        # # Configuration du gestionnaire de grille
        # self.rowconfigure(0, weight=1)
        # self.columnconfigure(0, weight=1)
        #
        # tk.Label(self, text="Firstname").grid(row=0)
        # tk.Label(self, text="Lastname").grid(row=1)
        # e1 = tk.Entry(self)
        # e2 = tk.Entry(self)
        # e1.grid(row=0, column=1)
        # e2.grid(row=1, column=1)
        #
        # label = tk.Label(
        #     self,
        #     text="Hello, Tkinter",
        #     foreground="black",  # Set the text color to white
        #     background="orange"  # Set the background color to black
        # )
        # label.grid(row=2, column=0)
        #
        # button = tk.Button(
        #     self,
        #     text="Click me!",
        #     width=25,
        #     height=5,
        #     bg="blue",
        #     fg="yellow",
        # )
        # button.grid(row=2, column=1)

        # label = tk.Label(self, text="This is the start page", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        #
        # button1 = tk.Button(self, text="Go to Page One",
        #                     command=lambda: controller.show_frame("TaskPage"))
        # button2 = tk.Button(self, text="Go to Page Two",
        #                     command=lambda: controller.show_frame("AddTaskPage"))
        # button1.pack()
        # button2.pack()


class TaskPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Task", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("DailyPage"))
        button.pack()


class AddTaskPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Create a task", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("DailyPage"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()



# import tkinter as tk
#
#
# class My_App(tk.Frame):
#
#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent)
#
#         # we need to set parent as a class attribute for later use
#         self.parent = parent
#         button1 = tk.Button(self.parent, text="Make window larger!", command = self.make_window_bigger)
#         button1.pack()
#
#         button2 = tk.Button(self.parent, text="Make window Smaller!", command = self.make_window_smaller)
#         button2.pack()
#
#     def make_window_bigger(self):
#         x = self.parent.winfo_height() + 10
#         y = self.parent.winfo_width() + 10
#         self.parent.geometry('{}x{}'.format(y, x))
#
#     def make_window_smaller(self):
#         x = self.parent.winfo_height() - 10
#         y = self.parent.winfo_width() - 10
#         self.parent.geometry('{}x{}'.format(y, x))
#
# root = tk.Tk()
# My_App(root)
# root.mainloop()


#
# import tkinter as tk
#
# window = tk.Tk()
#
#
# for i in range(3):
#     window.columnconfigure(i, weight=1, minsize=75)
#     window.rowconfigure(i, weight=1, minsize=50)
#
#     for j in range(0, 3):
#         frame = tk.Frame(
#             master=window,
#             relief=tk.GROOVE,
#             borderwidth=2
#         )
#         frame.grid(row=i, column=j, padx=5, pady=5)
#
#         btn = tk.Button(master=frame, text=f"Row {i}\nColumn {j}")
#         btn.pack(padx=5, pady=5)
#
# window.columnconfigure(0, weight=3, minsize=75)
# window.mainloop()
