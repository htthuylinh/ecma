from authfirebase import FirebaseAuth
from tkinter import *
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from datetime import datetime
from scipy import signal
from PIL import Image, ImageTk
import os
import pandas as pd
import paho.mqtt.client as mqtt
import numpy as np
import threading
import serialPage as sP
import importPage as iP


class FirstPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(self,
              text="ELECTROCHEMICAL MEASUREMENT APPLICATION",
              font=("TkDefaultFont", 14)).pack(pady=10)

        Button(self, text="OPEN DATA FOLDER", command=self.openFolder).place(x=1007, y=575)
        self.buttonSecondPage = Button(self, text="SERIAL", command=lambda: controller.show_frame(sP.SecondPage))
        self.buttonSecondPage.place(x=1131, y=575)
        self.buttonThirdPage = Button(self, text="IMPORT", command=lambda: controller.show_frame(iP.ThirdPage))
        self.buttonThirdPage.place(x=1182, y=575)
        Button(self, text="EXIT", command=lambda: controller.destroy()).place(x=1240, y=575)

        self.variable()
        self.add_logo("images/huet.png", 50, 10)
        self.add_logo("images/uet.png", 150, 10)
        self.add_logo("images/ccu.png", 250, 10)
        self.connectFrame()
        self.configureFrame()
        self.informationFrame()
        self.featureButtons()
        self.statusbar()
        self.dataTable()
        self.createFigure()

    def variable(self):
        self.idTreeView = []
        self.df = pd.DataFrame()
        self.client = mqtt.Client()
        self.times = []
        self.x = []
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.x4 = []
        self.x5 = []

        self.y = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []
        self.y5 = []
        self.number = 0

        self.statusESP = False

    def connectFrame(self):
        # Login
        frameLogin = LabelFrame(self, text="Log in")
        frameLogin.place(x=20, y=105, height=63, width=390)

        labelIPAdress = Label(frameLogin, text="IP address")
        labelIPAdress.place(x=5, y=0)
        self.entryIPAdress = Entry(frameLogin, width=11)
        self.entryIPAdress.place(x=7, y=20)
        self.entryIPAdress.delete(0, END)
        self.entryIPAdress.insert(0, "10.1.2.100")

        labelUsername = Label(frameLogin, text="Username")
        labelUsername.place(x=85, y=0)
        self.entryUsername = Entry(frameLogin, width=10)
        self.entryUsername.place(x=87, y=20)

        labelPassword = Label(frameLogin, text="Password")
        labelPassword.place(x=165, y=0)
        self.entryPassword = Entry(frameLogin, show="*", width=10)
        self.entryPassword.place(x=167, y=20)

        self.buttonLogin = Button(frameLogin,
                                  text="Login",
                                  command=self.thread_login,
                                  width=6)
        self.buttonLogin.place(x=255, y=10)

        self.buttonLogout = Button(frameLogin,
                                   text="Logout",
                                   command=self.logout,
                                   state=DISABLED,
                                   width=6)
        self.buttonLogout.place(x=315, y=10)

    def thread_login(self):
        """ This method will start the login process in a separate thread """
        # Start a new thread that will call the actual login method
        threading.Thread(target=self.login).start()

    def statusbar(self):
        self.statusVar = StringVar()
        self.statusVar.set("   No connection")
        self.statusBar = Label(self,
                               textvariable=self.statusVar,
                               relief=SUNKEN,
                               anchor="w",
                               fg="#FF0000")
        self.statusBar.pack(side=BOTTOM, fill=X)

        self.statusVarESP = StringVar()
        self.statusVarESP.set("   No connection")
        self.statusBarESP = Label(self,
                                  textvariable=self.statusVarESP,
                                  relief=SUNKEN,
                                  anchor="w",
                                  fg="#FF0000")
        self.statusBarESP.pack(side=BOTTOM, fill=X)

    def featureButtons(self):
        buttonStart = Button(self,
                             text="START",
                             width=6,
                             command=self.start)
        buttonStart.place(x=20, y=380)

        self.buttonSave = Button(self,
                                 text="SAVE DATA",
                                 width=10,
                                 command=self.save,
                                 state=DISABLED)
        self.buttonSave.place(x=80, y=380)

        self.buttonResetData = Button(self,
                                      text="RESET DATA",
                                      width=10,
                                      command=self.resetData)
        self.buttonResetData.place(x=170, y=380)

        self.buttonRestartESP = Button(self,
                                       text="RESTART ESP",
                                       width=10,
                                       command=self.restartESP,
                                       state=DISABLED)
        self.buttonRestartESP.place(x=260, y=380)

        buttonRestart = Button(self,
                               text="RESTART",
                               width=7,
                               command=self.restart)
        buttonRestart.place(x=350, y=380)

    def openFolder(self):
        try:
            if not os.path.exists("data"):
                os.mkdir("data")
            path = os.getcwd()
            os.startfile(path + "\data")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def configureFrame(self):
        # Configure Frame
        frameConfig = LabelFrame(self, text="Configure")
        frameConfig.place(x=20, y=170, height=200, width=215)

        labelStartV = Label(frameConfig, text="Start Voltage (mV)")
        labelStartV.place(x=10, y=5)
        self.entryStartV = Entry(frameConfig, width=7, justify="center")
        self.entryStartV.insert(0, "-200")
        self.entryStartV.place(x=150, y=5)

        labelEndV = Label(frameConfig, text="End Voltage (mV)")
        labelEndV.place(x=10, y=35)
        self.entryEndV = Entry(frameConfig, width=7, justify="center")
        self.entryEndV.insert(0, "600")
        self.entryEndV.place(x=150, y=35)

        labelStep = Label(frameConfig, text="Step (mV)")
        labelStep.place(x=10, y=65)
        self.entryStep = Entry(frameConfig, width=7, justify="center")
        self.entryStep.insert(0, "10")
        self.entryStep.place(x=150, y=65)

        labelScanRate = Label(frameConfig, text="Scan Rate (mV/s)")
        labelScanRate.place(x=10, y=95)
        self.entryScanRate = Entry(frameConfig, width=7, justify="center")
        self.entryScanRate.insert(0, "50")
        self.entryScanRate.place(x=150, y=95)

        labelRT = Label(frameConfig, text="Repeat Times")
        labelRT.place(x=10, y=125)
        self.entryRT = Entry(frameConfig, width=7, justify="center")
        self.entryRT.insert(0, "1")
        self.entryRT.place(x=150, y=125)

        labelCF = Label(frameConfig, text="Cutoff Frequence (Hz)")
        labelCF.place(x=10, y=155)
        self.entryCoFreq = Entry(frameConfig, width=7, justify="center")
        self.entryCoFreq.insert(0, "2")
        self.entryCoFreq.place(x=150, y=155)

    def informationFrame(self):
        # Information Frame
        frameInformationSave = LabelFrame(self, text="Information Save")
        frameInformationSave.place(x=250, y=170, height=200, width=160)

        labelToS = Label(frameInformationSave, text="Type of solution")
        labelToS.place(x=10, y=5)
        self.entryToS = Entry(frameInformationSave, width=20, justify="left")
        self.entryToS.place(x=10, y=30)

        labelMT = Label(frameInformationSave, text="Measurement times")
        labelMT.place(x=10, y=65)
        self.entryMT = Entry(frameInformationSave, width=20, justify="left")
        self.entryMT.place(x=10, y=90)

        labelConcentration = Label(frameInformationSave, text="Concentration")
        labelConcentration.place(x=10, y=125)
        self.entryConcentration = Label(frameInformationSave, text='None')
        self.entryConcentration.place(x=10, y=150)

    def add_logo(self, path, x, y):
        img = Image.open(path)
        resized_image = img.resize((90, 90))
        logo = Label(self, text="")
        logo.image = ImageTk.PhotoImage(resized_image)
        logo.configure(image=logo.image)
        logo.place(x=x, y=y)

    def dataTable(self):
        self.frameDataTable = LabelFrame(self, text="Data Table")
        self.frameDataTable.place(x=20, y=410, height=190, width=400)

        scrollbar = Scrollbar(self.frameDataTable, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.treeview = ttk.Treeview(self.frameDataTable,
                                     yscroll=scrollbar.set,
                                     show="headings")
        column_list = ["Potential (mV)", "Current (uA)", "Filtered current (uA)"]
        self.treeview["columns"] = column_list

        for column_name in column_list:
            self.treeview.heading(column_name, text=column_name)
            self.treeview.column(column_name, width=110, anchor=CENTER)

        # self.treeview.heading("#1", text=column_list[0])
        # self.treeview.column("#1", width=150, anchor=CENTER)

        self.treeview.pack(fill=BOTH, expand=True, side=TOP)
        scrollbar.configure(command=self.treeview.yview)

    def createFigure(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Realtime Cyclic Voltammentry Data")
        self.ax.set_xlabel("Potential (mV)")
        self.ax.set_ylabel("Current (uA)")
        self.listColor = ["red", "yellow", "purple", "blue", "green"]
        self.ax.grid()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().place(x=435, y=45, height=520, width=835)
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, padx=440)

    def runningPlot(self, dataRev):
        times = (int((int(self.entryEndV.get()) - int(self.entryStartV.get())) /
                     int(self.entryStep.get()) + 1)) * int(self.entryRT.get()) * 2
        times1 = times / int(self.entryRT.get())
        times2 = times / int(self.entryRT.get()) * 2
        times3 = times / int(self.entryRT.get()) * 3
        times4 = times / int(self.entryRT.get()) * 4

        if self.number < times1:
            self.plotData(self.listColor[0], self.x1, self.y1, dataRev)
            self.showPhone(1, self.number)
        elif self.number < times2 <= times:
            self.plotData(self.listColor[1], self.x2, self.y2, dataRev)
            self.showPhone(2, self.number, int(times1 + 1))
        elif self.number < times3 <= times:
            self.plotData(self.listColor[2], self.x3, self.y3, dataRev)
            self.showPhone(3, self.number, int(times2 + 1))
        elif self.number < times4 <= times:
            self.plotData(self.listColor[3], self.x4, self.y4, dataRev)
            self.showPhone(4, self.number, int(times3 + 1))
        elif self.number < times and times4 < times:
            self.plotData(self.listColor[4], self.x5, self.y5, dataRev)
            self.showPhone(5, self.number, int(times4 + 1))

    def plotData(self, set_color, x: list, y: list, dataRev):
        try:
            data = dataRev
            self.x.append(int(data[0]))
            self.y.append(float(data[1]))
            x.append(int(data[0]))
            y.append(float(data[1]))
            self.ax.plot(x, y, color=set_color, linewidth=1)
            self.canvas.draw()
            self.idTreeView.append(self.treeview.insert("",
                                                        END,
                                                        iid=self.number,
                                                        values=(self.x[self.number],
                                                                self.y[self.number])))
            self.treeview.see(self.idTreeView[-1])
            self.number += 1
            self.times.append(data[2])
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.restart()

    def lowpass(self, y, fc, fs):
        b, a = signal.butter(3, fc / (fs * 0.5), "low")
        filtered_current = signal.filtfilt(b, a, y, padlen=len(y) - 1)
        return filtered_current

    def updateDataTable(self, turn, filtered):
        for i in range(len(filtered) * turn, len(filtered) * (turn + 1)):
            temp = self.treeview.item(i, "values")
            self.treeview.item(i, values=(temp[0], temp[1], filtered[i - len(filtered) * turn]))

    def showPhone(self, num, number, times=1):
        if number == times:
            self.client.publish("CV/min_v_" + str(num), "processing")
            self.client.publish("CV/min_a_" + str(num), "processing")
            self.client.publish("CV/max_v_" + str(num), "processing")
            self.client.publish("CV/max_a_" + str(num), "processing")

    def calculatecM(self):
        newWindow = Toplevel()
        newWindow.title("Calculate cM")
        newWindow.geometry("300x50")

        labela = Label(newWindow, text="coefficient a")
        labela.place(x=5, y=0)
        entrya = Entry(newWindow, width=13)
        entrya.place(x=7, y=20)
        entrya.delete(0, END)
        entrya.insert(0, "0.64755")  #5.64024

        labelb = Label(newWindow, text="coefficient b")
        labelb.place(x=105, y=0)
        entryb = Entry(newWindow, width=13)
        entryb.place(x=107, y=20)
        entryb.delete(0, END)
        entryb.insert(0, "11.05801")  #345.32

        def calculate():
            a = float(entrya.get())
            b = float(entryb.get())

            cm_list = []

            def cM(y, a, b):
                x = (y - b) / a
                return round(x, 2)

            print(self.max_vl)
            print(self.min_vl)
            print(self.delta_u)
            text = f'{cM(max(self.max_vl), a, b)}|{max(self.max_vl)}_{min(self.min_vl)}?{max(self.delta_u)}'
            print(text)

            for i, phan_tu in enumerate(self.max_vl):
                cm = cM(phan_tu, a, b)
                self.client.publish(f"CV/cm_{i + 1}", cm)
                cm_list.append(cm)
            self.entryConcentration.configure(text=', '.join(str(i) for i in cm_list))
            print(text)
            self.client.publish("CV/lcd", text)

            newWindow.destroy()
            messagebox.showinfo("Notification", "Complete the measurement")

        buttonCal = Button(newWindow, text="Calculate", command=calculate)
        buttonCal.place(x=200, y=15)

    def endingPlot(self):
        pd.DataFrame(self.times).to_csv("data1.csv")
        self.canvas.get_tk_widget().destroy()
        self.fig_lowpass = Figure()
        self.ax_lowpass = self.fig_lowpass.add_subplot(111)
        self.ax_lowpass.set_title("Realtime Cyclic Voltammentry Data")
        self.ax_lowpass.set_xlabel("Potential (mV)")
        self.ax_lowpass.set_ylabel("Current (uA)")
        self.ax_lowpass.set_xlim(int(self.entryStartV.get()) - 25, int(self.entryEndV.get()) + 25)
        self.ax_lowpass.xaxis.set_ticks(np.arange(int(self.entryStartV.get()), int(self.entryEndV.get()) + 1, 100))
        self.ax_lowpass.grid()

        self.canvas = FigureCanvasTkAgg(self.fig_lowpass, self)
        self.canvas.get_tk_widget().place(x=435, y=45, height=520, width=835)
        self.canvas.draw()

        fc = float(self.entryCoFreq.get())
        sr = int(self.entryScanRate.get())
        columnName = ["mV_1", "uA_1", "filter_uA_1",
                      "mV_2", "uA_2", "filter_uA_2",
                      "mV_3", "uA_3", "filter_uA_3",
                      "mV_4", "uA_4", "filter_uA_4",
                      "mV_5", "uA_5", "filter_uA_5"]
        listValues = [[self.x1, self.y1],
                      [self.x2, self.y2],
                      [self.x3, self.y3],
                      [self.x4, self.y4],
                      [self.x5, self.y5]]

        self.max_vl = []
        self.min_vl = []
        self.delta_u = []

        for i in range(len(listValues)):
            if not listValues[i][0]:
                break
            else:
                listValues[i].append(self.lowpass(listValues[i][1], fc, sr))
                # self.ax.plot(listValues[i][0],
                #              listValues[i][2],
                #              color=self.listColor[i],
                #              linestyle="dotted",
                #              linewidth=2)
                self.ax_lowpass.plot(listValues[i][0],
                                     listValues[i][2],
                                     color=self.listColor[i],
                                     linewidth=2)
                self.canvas.draw()
                self.updateDataTable(i, listValues[i][2])
                min_v = listValues[i][0][listValues[i][2].tolist().index(min(listValues[i][2]))]
                max_v = listValues[i][0][listValues[i][2].tolist().index(max(listValues[i][2]))]
                self.client.publish("CV/min_v_" + str(i + 1), min_v)
                self.client.publish("CV/min_i_" + str(i + 1), round(min(listValues[i][2]), 2))
                self.client.publish("CV/max_v_" + str(i + 1), max_v)
                self.client.publish("CV/max_i_" + str(i + 1), round(max(listValues[i][2]), 2))
                self.delta_u.append(abs(max_v - min_v))
                self.client.publish("CV/delta_v_" + str(i + 1), abs(max_v - min_v))

                self.max_vl.append(round(max(listValues[i][2]), 2))
                self.min_vl.append(round(min(listValues[i][2]), 2))

                if i == 1:
                    temp = np.append(listValues[i - 1], listValues[i], axis=0)
                elif i > 1:
                    temp = np.append(temp, listValues[i], axis=0)
                else:
                    temp = listValues[i]

        if not os.path.exists("temp"):
            os.mkdir("temp")
        self.fig_lowpass.savefig("temp/_lowpass.png", dpi=300)
        if FirebaseAuth.firebase():
            st = FirebaseAuth.firebase().storage()
            st.child("injoker.png").put("temp/_lowpass.png")
            import shutil
            shutil.rmtree("temp")

        self.calculatecM()
        self.df = pd.DataFrame(np.column_stack(temp), columns=columnName[:int(self.entryRT.get()) * 3])
        self.buttonSave.configure(state=NORMAL)
        self.buttonResetData.configure(state=NORMAL)

    def start(self):
        self.client.publish('CV/wirelessact', 'processing')
        if self.statusESP == True:
            try:
                if int(self.entryStartV.get()) < -825:
                    messagebox.showerror("Error Potentiosat",
                                         "StartVoltage >= -825mV")
                elif int(self.entryEndV.get()) > 825:
                    messagebox.showerror("Error Potentiosat",
                                         "StartVoltage <= 825mV")
                elif int(self.entryEndV.get()) < int(self.entryStartV.get()):
                    messagebox.showerror("Error Potentiosat",
                                         "EndVoltage > Start Voltage")
                elif int(self.entryRT.get()) > 5 or int(self.entryRT.get()) < 1:
                    messagebox.showerror("Error Potentiosat",
                                         "1 <= RepeatTimes <= 5")
                elif float(self.entryCoFreq.get()) >= int(self.entryScanRate.get()) / 2:
                    messagebox.showerror("Error Potentiosat",
                                         "1 <= Cutoff Frequence < Scan Rate/2")
                else:
                    command = self.entryStartV.get() + "|" + self.entryEndV.get() + "_" + self.entryStep.get() + "?" + str(
                        int(int(self.entryScanRate.get()) / 2)) + "#" + self.entryRT.get()
                    self.client.publish("CV/command", command.encode(encoding='ascii', errors='strict'))
                    self.client.publish("CV/status_plot", "run")

                    self.buttonSave.configure(state=DISABLED)
                    self.buttonResetData.configure(state=DISABLED)

                    self.ax.set_xlim(int(self.entryStartV.get()) - 25, int(self.entryEndV.get()) + 25)
                    self.ax.xaxis.set_ticks(np.arange(int(self.entryStartV.get()), int(self.entryEndV.get()) + 1, 100))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "ESP is not ready to use")

    def save(self):
        now = datetime.now()
        dt_str = now.strftime("%H_%M_%S")
        # date_str = now.strftime("%d_%m_%Y")
        patch1 = self.entryToS.get()
        patch2 = self.entryMT.get()
        patch = "data/" + patch1 + "/" + patch2 + "/"
        if not self.df.empty:
            if not os.path.exists("data"):
                os.mkdir("data")
            if not os.path.exists("data/" + patch1):
                os.mkdir("data/" + patch1)
            if not os.path.exists(patch):
                os.mkdir(patch)
            self.df.to_csv(patch + dt_str + ".csv", index=False)
            self.fig.savefig(patch + dt_str + ".png", dpi=300)
            self.fig_lowpass.savefig(patch + dt_str + "_lowpass.png", dpi=300)
            self.df = pd.DataFrame()
            messagebox.showinfo("Notification", "File is saved successfully")

    def login(self):
        # try:
        username = self.entryUsername.get()
        password = self.entryPassword.get()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        try:
            self.client.connect(self.entryIPAdress.get(), 1883)
            self.client.loop_start()
            self.buttonSecondPage.configure(state=DISABLED)
            self.buttonThirdPage.configure(state=DISABLED)
        except Exception as e:
            messagebox.showinfo("Notification", str(e))

    # except Exception as e:
    #     messagebox.showerror("Error", "Login failed\n"+str(e))

    def logout(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.client = mqtt.Client()

        self.statusVar.set("   No connection")
        self.statusBar.configure(fg="#FF0000")

        self.statusVarESP.set("   No connection")
        self.statusBarESP.configure(fg="#FF0000")
        self.statusESP = False

        self.buttonSecondPage.configure(state=NORMAL)
        self.buttonThirdPage.configure(state=NORMAL)

    def on_message(self, client, userdata, message):
        if message.topic == "CV/statusESP":
            if message.payload.decode() == "ready":
                self.statusVarESP.set("   ESP is ready to use")
                self.statusBarESP.configure(fg="#008000")
                self.statusESP = True
            elif message.payload.decode() == "notready":
                self.statusVarESP.set("   Waiting response from ESP")
                self.statusBarESP.configure(fg="#FFA500")
                self.statusESP = False
            elif message.payload.decode() == "restarted":
                print("ok")

        if message.topic == "CV/values":
            data_rev = message.payload.decode().split(";")
            self.runningPlot(data_rev)

        if message.topic == "CV/status_plot":
            if message.payload.decode() == "done":
                self.endingPlot()

        if message.topic == "CV/wirelessact":
            if message.payload.decode() == "start":
                self.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("CV/values")
            client.subscribe("CV/status_plot")
            client.subscribe("CV/statusESP")
            client.subscribe("CV/wirelessact")
            client.publish("CV/statusESP", "checking")

            messagebox.showinfo("Notification", "Log in successfully\nConnected to MQTT broker")

            self.entryIPAdress.configure(state=DISABLED)
            self.entryUsername.configure(state=DISABLED)
            self.entryPassword.configure(state=DISABLED)
            self.buttonLogin.configure(state=DISABLED)
            self.buttonLogout.configure(state=NORMAL)
            self.buttonRestartESP.configure(state=NORMAL)

            self.statusVar.set(f"   Connect to MQTT server at {self.entryIPAdress.get()}:1883")
            self.statusBar.configure(fg="#008000")

            self.statusVarESP.set("   Waiting response from ESP")
            self.statusBarESP.configure(fg="#FFA500")
            self.statusESP = False

        else:
            client.loop_stop()
            client.disconnect()

    def on_disconnect(self, client, userdata, rc):
        self.statusVarESP.set("   No connection")
        self.statusBarESP.configure(fg="#FF0000")
        self.entryIPAdress.configure(state=NORMAL)
        self.entryUsername.configure(state=NORMAL)
        self.entryPassword.configure(state=NORMAL)
        self.buttonLogin.configure(state=NORMAL)
        self.buttonLogout.configure(state=DISABLED)
        self.buttonRestartESP.configure(state=DISABLED)
        print(client, userdata, rc)

    def resetData(self):
        self.canvas.get_tk_widget().destroy()
        self.frameDataTable.destroy()
        self.toolbar.destroy()
        self.buttonSave.configure(state=DISABLED)
        self.entryConcentration.configure(text='None')
        self.times = []

        self.idTreeView = []
        self.df = pd.DataFrame()

        self.x = []
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.x4 = []
        self.x5 = []

        self.y = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []
        self.y5 = []
        self.number = 0

        self.dataTable()
        self.createFigure()

    def restartESP(self):
        self.client.publish("CV/statusESP", "restart")
        self.statusVarESP.set("   Waiting response from ESP")
        self.statusBarESP.configure(fg="#FFA500")
        self.statusESP = False

        self.buttonResetData.configure(state=NORMAL)

    def restart(self):
        try:
            self.restartESP()
        except:
            pass
        self.logout()
        self.resetData()

    def run_after(self, ms: int, command):
        run_after = self.after(ms, command)
        return run_after

    def cancel_after(self, id):
        self.after_cancel(id)


# class ThirdPage(Frame):
#     def __init__(self, parent, controller):
#         Frame.__init__(self, parent)

class Application(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        window = Frame(self)
        window.pack()

        window.grid_columnconfigure(0, minsize=1300)
        window.grid_rowconfigure(0, minsize=650)

        self.frames = {}
        for F in (FirstPage, sP.SecondPage, iP.ThirdPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(FirstPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
