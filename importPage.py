from tkinter import *
from tkinter import messagebox, ttk, filedialog

import numpy as np
from scipy import signal
from pathlib import Path
import pandas as pd
import os
import wirelessPage as wP
import serialPage as sP
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from authfirebase import FirebaseAuth
# 1200x650

class ThirdPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(self,
              text="ELECTROCHEMICAL MEASUREMENT APPLICATION",
              font=("TkDefaultFont", 14)).pack(pady=10)

        Button(self, text="OPEN DATA FOLDER", command=self.openFolder).place(x=999, y=595)
        self.buttonFirstPage = Button(self, text="WIRELESS", command=lambda: controller.show_frame(wP.FirstPage))
        self.buttonFirstPage.place(x=1123, y=595)
        self.buttonThirdPage = Button(self, text="SERIAL", command=lambda: controller.show_frame(sP.SecondPage))
        self.buttonThirdPage.place(x=1189, y=595)
        Button(self, text="EXIT", command=lambda: controller.destroy()).place(x=1240, y=595)

        self.fileOptionFrame()
        self.minMaxFrame()

        self.frameDataTable = LabelFrame(self, text="Data Table")
        self.frameDataTable.place(x=435, y=45, height=520, width=835)

        wP.FirstPage.add_logo(self, "images/huet.png", 120, 10)
        wP.FirstPage.add_logo(self, "images/uet.png", 220, 10)

    def fileOptionFrame(self):
        frameOperationsFile = LabelFrame(self, text="File Manipulation Options")
        frameOperationsFile.place(x=20, y=105, height=123, width=350)

        buttonBrowseFile = Button(frameOperationsFile, text="Browse Data Set", command=self.openfile)
        buttonBrowseFile.place(x=5, y=0)

        self.labelFileName = Label(frameOperationsFile, text="File not choosen")
        self.labelFileName.place(x=110, y=3)

        self.buttonLoadFile = Button(frameOperationsFile, text="Load Data Set", width=12, state=DISABLED, command=self.loadDataSet)
        self.buttonLoadFile.place(x=5, y=35)
        
        self.buttonClearFile = Button(frameOperationsFile, text="Clear Data Set", width=12, state=DISABLED, command=self.clearDataSet)
        self.buttonClearFile.place(x=110, y=35)

        self.buttoncalculateCM = Button(frameOperationsFile, text="Calculate CM", width=12, state=DISABLED, command=self.calculatecM)
        self.buttoncalculateCM.place(x=5, y=70)

        self.buttonSend = Button(frameOperationsFile, text="Send Values", width=14, state=DISABLED,
                                 command=lambda:self.sendValues("minmax", self.df))
        self.buttonSend.place(x=215, y=35)

        self.buttonPlot = Button(frameOperationsFile, text="Plot Filtered Figure", width=14, state=DISABLED, command=self.plotFigure)
        self.buttonPlot.place(x=110, y=70)

    def openfile(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Comma Separated Values", ".csv")])
        self.labelFileName.configure(text=os.path.basename(self.filepath))
        self.buttonLoadFile.configure(state=NORMAL)

        self.clearMinMax()
        self.clearDataSet()

    def loadDataSet(self):
        self.buttonClearFile.configure(state=NORMAL)
        self.buttonSend.configure(state=NORMAL)
        self.buttonPlot.configure(state=NORMAL)
        self.buttonLoadFile.configure(state=DISABLED)

        self.df = pd.read_csv(self.filepath)

        scrollbarV=Scrollbar(self.frameDataTable, orient="vertical")
        scrollbarV.pack(side=RIGHT, fill=Y)

        scrollbarH=Scrollbar(self.frameDataTable, orient="horizontal")
        scrollbarH.pack(side=BOTTOM, fill=X)

        self.treeview = ttk.Treeview(self.frameDataTable,
                                     yscrollcommand=scrollbarV.set,
                                     xscrollcommand=scrollbarH.set,
                                     show="headings")
        column_list = self.df.columns.to_list()
        self.treeview["columns"] = column_list

        for column_name in column_list:
            self.treeview.heading(column_name, text=column_name)
            self.treeview.column(column_name, width=80, anchor=CENTER)

        for i, row in self.df.iterrows():
            self.treeview.insert("", END, values=tuple(row.values.reshape(1, -1)[0]))

        self.treeview.pack(fill=BOTH, expand=TRUE)

        scrollbarV.configure(command=self.treeview.yview)
        scrollbarH.configure(command=self.treeview.xview)

        self.loadMinMax()

    def minMaxFrame(self):
        self.frameMinMax = LabelFrame(self, text="Min Max Table")
        self.frameMinMax.place(x=20, y=250, height=270, width=400)

    def loadMinMax(self):
        self.buttoncalculateCM.configure(state=NORMAL)

        list_index = []
        min_values = []
        max_values = []

        column_list = self.df.columns.to_list()
        for i in range(int(len(column_list)/3)):
            list_index.append("V"+str(i+1))
            list_index.append("I"+str(i+1))
            v = self.df[column_list[(i+1)*3-3]].values
            a = self.df[column_list[(i+1)*3-1]].values
            min_values.append(round(v[a.tolist().index(min(a))], 3))
            min_values.append(round(min(a), 3))
            max_values.append(round(v[a.tolist().index(max(a))], 3))
            max_values.append(round(max(a), 3))

        self.datas = {"name_values":list_index, "min":min_values, "max":max_values}
        self.df_new = pd.DataFrame(self.datas)

        scrollbarV1=Scrollbar(self.frameMinMax, orient="vertical")
        scrollbarV1.pack(side=RIGHT, fill=Y)

        scrollbarH1=Scrollbar(self.frameMinMax, orient="horizontal")
        scrollbarH1.pack(side=BOTTOM, fill=X)

        self.treeview1 = ttk.Treeview(self.frameMinMax,
                                     yscrollcommand=scrollbarV1.set,
                                     xscrollcommand=scrollbarH1.set,
                                     show="headings")
        column_list = self.df_new.columns.to_list()
        self.treeview1["columns"] = column_list
        self.treeview1.heading(column_list[0], text=column_list[0])
        self.treeview1.column(column_list[0], width=80, anchor=CENTER)

        for column_name in column_list[1:]:
            self.treeview1.heading(column_name, text=column_name)
            self.treeview1.column(column_name, width=80, anchor=W)

        for i, row in self.df_new.iterrows():
            self.treeview1.insert("", END, values=tuple(row.values.reshape(1, -1)[0]))

        self.treeview1.pack(fill=BOTH, expand=TRUE)

        scrollbarV1.configure(command=self.treeview1.yview)
        scrollbarH1.configure(command=self.treeview1.xview)

        self.df_new.to_csv(str(Path(self.filepath).parent) + "/minmaxtable.csv", index=False)

    def plotFigure(self):
        listColor = ["red", "yellow", "purple", "blue", "green"]
        plt.rcParams["font.family"] = "Arial"

        fig, ax = plt.subplots(1, 2, figsize=(22, 9))

        # ax[0].set_title("(a)\n",
        #                   fontsize=24,
        #                   loc='left')
        # ax[1].set_title("(b)\n",
        #                   fontsize=24,
        #                   loc='left')

        for _ in range(2):
            ax[_].set_xlabel("Potential (mV)", fontsize=24)
            ax[_].set_ylabel("Current (uA)", fontsize=24)
            ax[_].tick_params(axis='both', which='major', labelsize=24)
            ax[_].grid()

        # plt.title("Wired (A)")
        # plt.xlabel("Potential (mV)")
        # plt.ylabel("Current (uA)")
        # plt.grid()

        column_list = self.df.columns.to_list()
        # min_i = []
        # max_i = []
        for _ in range(int(len(column_list)/3)):
            if _>0:
                v = self.df[column_list[(_+1)*3-3]].values
                i = self.df[column_list[(_+1)*3-1]].values
                i_raw = self.df[column_list[(_+1)*3-2]].values
                # plt.plot(v, i, color=listColor[_])

                ax[0].plot(v, i_raw, color=listColor[_])
                ax[1].plot(v, i, color=listColor[_])

                # min_i.append(int(v[i.tolist().index(min(i))]))
                # max_i.append(int(v[i.tolist().index(max(i))]))

        # axis[1].axvline(x=max(max_i), color='black', linestyle="dashdot")
        # axis[1].axvline(x=min(min_i), color='black', linestyle="dashdot")
        fig.savefig(str(Path(self.filepath).parent)+"/ok2.jpg", dpi=300)
        plt.show()

    def sendValues(self, choice, data):
        newWindow = Toplevel()
        newWindow.title("Login to send min max values")
        newWindow.geometry("300x50")

        labelIPAdress = Label(newWindow, text="IP address")
        labelIPAdress.place(x=5, y=0)
        entryIPAdress = Entry(newWindow, width=11)
        entryIPAdress.place(x=7, y=20)
        entryIPAdress.delete(0,END)
        entryIPAdress.insert(0,"10.1.2.100")

        labelUsername = Label(newWindow, text="Username")
        labelUsername.place(x=85, y=0)
        entryUsername = Entry(newWindow, width=10)
        entryUsername.place(x=87, y=20)
        entryUsername.delete(0,END)
        entryUsername.insert(0,"user2")

        labelPassword = Label(newWindow, text="Password")
        labelPassword.place(x=165, y=0)
        entryPassword = Entry(newWindow, show="*", width=10)
        entryPassword.place(x=167, y=20)
        entryPassword.delete(0,END)
        entryPassword.insert(0,"okong")
        client = mqtt.Client()

        buttonSend = Button(newWindow,
                            text="Login",
                            width=6)
        buttonSend.place(x=238, y=13)

        def login():
            try:
                username = entryUsername.get()
                password = entryPassword.get()
                client.username_pw_set(username, password)
                client.on_connect = on_connect
                client.connect(entryIPAdress.get(), 1883)
                client.loop_start()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe("CV/values")
                client.subscribe("CV/status_plot")
                client.subscribe("CV/statusESP")
                client.publish("CV/statusESP", "checking")
                print('ok')
                buttonSend.configure(command=send,
                                     text="Send")

            else:
                client.loop_stop()
                client.disconnect()
                newWindow.destroy()

        def send():
            if choice == "minmax":
                column_list = data.columns.to_list()
                for _ in range(int(len(column_list)/3)):
                    v = data[column_list[(_+1)*3-3]].values
                    i = data[column_list[(_+1)*3-1]].values
                    client.publish(f"CV/min_v_{str(_+1)}", int(v[i.tolist().index(min(i))]))
                    client.publish(f"CV/min_i_{str(_+1)}", round(min(i), 2))
                    client.publish(f"CV/max_v_{str(_+1)}", int(v[i.tolist().index(max(i))]))
                    client.publish(f"CV/max_i_{str(_+1)}", round(max(i), 2))

                if FirebaseAuth.firebase():
                    filelist = os.listdir(str(Path(self.filepath).parent))
                    for _ in filelist:
                        if _.endswith("_lowpass.png"):
                            st = FirebaseAuth.firebase().storage()
                            st.child("injoker.png").put(f"{str(Path(self.filepath).parent)}/{_}")

                newWindow.destroy()
                messagebox.showinfo("Notification", "Complete")
            elif choice == "cm":
                client.publish("CV/cm", round(np.average(data.cmmax.values), 2))

                newWindow.destroy()
                messagebox.showinfo("Notification", "Complete")

        buttonSend.configure(command=login)
    
    def clearDataSet(self):
        self.clearMinMax()

        self.buttonClearFile.configure(state=DISABLED)
        self.buttoncalculateCM.configure(state=DISABLED)
        self.buttonSend.configure(state=DISABLED)
        self.buttonPlot.configure(state=DISABLED)
        self.buttonLoadFile.configure(state=NORMAL)

        self.frameDataTable.destroy()
        self.frameDataTable = LabelFrame(self, text="Data Table")
        self.frameDataTable.place(x=435, y=45, height=520, width=835)

        self.clearMinMax()

    def clearMinMax(self):
        self.buttoncalculateCM.configure(state=DISABLED)

        self.frameMinMax.destroy()

        self.frameMinMax = LabelFrame(self, text="Min Max Table")
        self.frameMinMax.place(x=20, y=250, height=270, width=400)

    def openFolder(self):
        try:
            if not os.path.exists("data"):
                os.mkdir("data")
            path = os.getcwd()
            os.startfile(path+"\data")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculatecM(self):
        newWindow = Toplevel()
        newWindow.title("Calculate cM")
        newWindow.geometry("300x50")

        labela = Label(newWindow, text="coefficient a")
        labela.place(x=5, y=0)
        entrya = Entry(newWindow, width=13)
        entrya.place(x=7, y=20)
        entrya.delete(0, END)
        entrya.insert(0, "2") #5.64024

        labelb = Label(newWindow, text="coefficient b")
        labelb.place(x=105, y=0)
        entryb = Entry(newWindow, width=13)
        entryb.place(x=107, y=20)
        entryb.delete(0, END)
        entryb.insert(0, "3") #345.32

        def calculate():
            a = float(entrya.get())
            b = float(entryb.get())
            cMmin = []
            cMmax = []

            def timx(y, a, b):
                x = (y-b)/a
                return round(x, 3)
            
            for i in range(len(self.datas["min"])):
                if i%2 != 0:
                    cMmin.append(timx(self.datas["min"][i], a, b))
                    cMmax.append(timx(self.datas["max"][i], a, b))

            min_values_ = [round(self.datas["min"][i], 3) for i in range(len(self.datas["min"])) if self.datas["min"][i] % 2 != 0]
            max_values_ = [round(self.datas["max"][i], 3) for i in range(len(self.datas["max"])) if self.datas["max"][i] % 2 != 0]
            
            minfig = plt.figure("min fig")
            plt.plot(cMmin, min_values_, "-o")
            for i, j in zip(cMmin, min_values_):
                plt.annotate('(%s, %s)' % (i, j), xy=(i, j), size=12, ha='center')
            plt.ylim(min(min_values_)-2, max(min_values_)+2)
            minfig.show()

            maxfig = plt.figure("max fig")
            plt.plot(cMmax, max_values_, "-o", color="red")
            for i, j in zip(cMmax, max_values_):
                plt.annotate('(%s, %s)' % (i, j), xy=(i, j), size=12, ha='center')
            plt.ylim(min(max_values_)-2, max(max_values_)+2)
            maxfig.show()

            datas = {"cmmin":cMmin, "Imin":min_values_, "cmmax":cMmax, "Imax":max_values_}
            df = pd.DataFrame(datas)
            df.to_csv(str(Path(self.filepath).parent)+"/concentration.csv", index=False)
            self.sendValues("cm", df)
            newWindow.destroy()

        buttonCal = Button(newWindow, text="Calculate", command=calculate)
        buttonCal.place(x=200, y=15)