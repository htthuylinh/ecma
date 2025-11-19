from tkinter import *
from tkinter import messagebox, ttk, _setit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from datetime import datetime
from scipy import signal
import pandas as pd
import serial
import serial.tools.list_ports
import os
import time
import numpy as np
import wirelessPage as wP
import importPage as iP
# 1200x650

class SecondPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(self,
              text="ELECTROCHEMICAL MEASUREMENT APPLICATION",
              font=("TkDefaultFont", 14)).pack(pady=10)

        Button(self, text="OPEN DATA FOLDER", command=self.openFolder).place(x=991, y=595)
        self.buttonFirstPage = Button(self, text="WIRELESS", command=lambda: controller.show_frame(wP.FirstPage))
        self.buttonFirstPage.place(x=1115, y=595)
        self.buttonThirdPage = Button(self, text="IMPORT", command=lambda: controller.show_frame(iP.ThirdPage))
        self.buttonThirdPage.place(x=1182, y=595)
        Button(self, text="EXIT", command=lambda: controller.destroy()).place(x=1240, y=595)
        # lambda: controller.show_frame(SecondPage))

        self.statusVar = StringVar()
        self.statusVar.set("   No connection")
        self.statusBar = Label(self,
                               textvariable=self.statusVar,
                               relief=SUNKEN,
                               anchor="w",
                               fg="#FF0000")
        self.statusBar.pack(side=BOTTOM, fill=X)

        self.variable()
        wP.FirstPage.add_logo(self, "images/huet.png", 50, 10)
        wP.FirstPage.add_logo(self, "images/uet.png", 150, 10)
        wP.FirstPage.add_logo(self, "images/ccu.png", 250, 10)
        self.connectFrame()
        self.configureFrame()
        self.informationFrame()
        self.featureButtons()
        self.dataTable()
        self.createFigure()

    def variable(self):
        self.ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            self.ports.append(port)

        self.idTreeView = []
        self.df = pd.DataFrame()
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

        self.statusPlot = False
        self.statusConnect = False
        self.number = 0

    def connectFrame(self):
        frameLogin = LabelFrame(self, text="Connect to Serial")
        frameLogin.place(x=20, y=105, height=63, width=390)

        self.buttonConnectPORT = Button(frameLogin,
                                   text="Connect",
                                   command=self.connectToPORT)
        self.buttonConnectPORT.place(x=20, y=5)
        
        self.buttonDisconnectPORT = Button(frameLogin,
                                      text="Disconnect",
                                      command=self.disconnectToPORT,
                                      state=DISABLED)
        self.buttonDisconnectPORT.place(x=85, y=5)

        self.buttonReloadListPORT = Button(frameLogin,
                                      text="Reload list PORT",
                                      command=self.reloadListPORT)
        self.buttonReloadListPORT.place(x=165, y=5)

        self.optionVar = StringVar(frameLogin)
        self.optionMenu = ttk.OptionMenu(frameLogin,
                                         self.optionVar,
                                         "Not Selected",
                                         *self.ports)
        self.optionMenu.place(x=275, y=5)

    def featureButtons(self):
        buttonStart = Button(self,
                             text="START",
                             width=6,
                             command=self.start)
        buttonStart.place(x=20, y=380)

        self.buttonPause_Continue = Button(self,
                                           text="PAUSE",
                                           width=10,
                                           command=self.pause,
                                           state=DISABLED)
        self.buttonPause_Continue.place(x=80, y=380)

        self.buttonSave = Button(self,
                              text="SAVE",
                              width=6,
                              command=self.save,
                              state=DISABLED)
        self.buttonSave.place(x=170, y=380)

        buttonResetData = Button(self,
                              text="RESET DATA",
                              width=12,
                              command=self.resetData)
        buttonResetData.place(x=230, y=380)

        buttonRestart = Button(self,
                              text="RESTART",
                              width=7,
                              command=self.restart)
        buttonRestart.place(x=335, y=380)

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

    def dataTable(self):
        self.frameDataTable = LabelFrame(self, text="Data Table")
        self.frameDataTable.place(x=20, y=410, height=210, width=400)

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
        self.canvas.get_tk_widget().place(x=435, y=45, height=540, width=835)
        self.canvas.draw()
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, padx=440)

    def runningPlot(self):
        times = (int((int(self.entryEndV.get())-int(self.entryStartV.get()))/
                 int(self.entryStep.get())+1))*int(self.entryRT.get())*2
        times1 = times/int(self.entryRT.get())
        times2 = times/int(self.entryRT.get())*2
        times3 = times/int(self.entryRT.get())*3
        times4 = times/int(self.entryRT.get())*4

        if self.statusPlot==True:
            if self.number<times1:
                self.plotData(self.listColor[0], self.x1, self.y1)
            elif self.number<times2 and times>=times2:
                self.plotData(self.listColor[1], self.x2, self.y2)
            elif self.number<times3 and times>=times3:
                self.plotData(self.listColor[2], self.x3, self.y3)
            elif self.number<times4 and times>=times4:
                self.plotData(self.listColor[3], self.x4, self.y4)
            elif self.number<times and times4<times:
                self.plotData(self.listColor[4], self.x5, self.y5)
            else:
                # self.plotData(self.listColor[4], self.x5, self.y5)
                self.cancel_after(self.runAfter)
                self.statusPlot = False
                self.endingPlot()
                
    def plotData(self, set_color, x:list, y:list):
        try:
            data = self.ser.readline().decode().split(";")
            self.x.append(int(data[0]))
            self.y.append(float(data[1]))
            self.times.append(data[2].replace("\r\n",""))
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
            self.number+=1
            self.runAfter = self.run_after(10, self.runningPlot)
        except:
            self.number = 0
            self.runAfter = self.run_after(10, self.runningPlot)
        
    def lowpass(self, y, fc, fs):
        b, a = signal.butter(3, fc/(fs*0.5), "low")
        filtered_current = signal.filtfilt(b, a, y, padlen=len(y)-1)
        return filtered_current

    def endingPlot(self):
        print(self.times)
        pd.DataFrame(self.times).to_csv("data1.csv")
        self.canvas.get_tk_widget().destroy()
        self.fig_lowpass = Figure()
        self.ax_lowpass = self.fig_lowpass.add_subplot(111)
        self.ax_lowpass.set_title("Realtime Cyclic Voltammentry Data")
        self.ax_lowpass.set_xlabel("Potential (mV)")
        self.ax_lowpass.set_ylabel("Current (uA)")
        self.ax_lowpass.set_xlim(int(self.entryStartV.get())-25, int(self.entryEndV.get())+25)
        self.ax_lowpass.xaxis.set_ticks(np.arange(int(self.entryStartV.get()), int(self.entryEndV.get())+1, 100))
        self.ax_lowpass.grid()

        self.canvas = FigureCanvasTkAgg(self.fig_lowpass, self)
        self.canvas.get_tk_widget().place(x=435, y=45, height=540, width=835)
        self.canvas.draw()

        fc = float(self.entryCoFreq.get())
        fs = int(self.entryScanRate.get())
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
        for i in range(len(listValues)):
            if not listValues[i][0]:
                break
            else:
                listValues[i].append(self.lowpass(listValues[i][1], fc, fs))
                self.ax_lowpass.plot(listValues[i][0],
                                     listValues[i][2],
                                     color=self.listColor[i],
                                     linewidth=2)
                self.canvas.draw()
                self.updateDataTable(i, listValues[i][2])
                self.max_vl.append(round(max(listValues[i][2]), 2))
                if i==1:
                    temp = np.append(listValues[i-1], listValues[i], axis=0)
                elif i>1:
                    temp = np.append(temp, listValues[i], axis=0)
                else:
                    temp = listValues[i]
        self.df = pd.DataFrame(np.column_stack(temp), columns=columnName[:int(self.entryRT.get())*3])
        self.buttonSave.configure(state=NORMAL)
        self.calculatecM()
        # messagebox.showinfo("Nofitication", "Complete the measurement")
       
    def updateDataTable(self, turn, filtered):
        for i in range(len(filtered)*turn, len(filtered)*(turn+1)):
            temp = self.treeview.item(i, "values")
            self.treeview.item(i, values=(temp[0], temp[1], filtered[i-len(filtered)*turn]))


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

            cm_list = []

            def cM(y, a, b):
                x = (y-b)/a
                return round(x, 2)

            for i, phan_tu in enumerate(self.max_vl):
                cm = cM(phan_tu, a, b)

                cm_list.append(cm)
            self.entryConcentration.configure(text=', '.join(str(i) for i in cm_list))
            newWindow.destroy()
            messagebox.showinfo("Notification", "Complete the measurement")

        buttonCal = Button(newWindow, text="Calculate", command=calculate)
        buttonCal.place(x=200, y=15)

    def connectToPORT(self):
        try:
            self.ser = serial.Serial(self.optionVar.get(), 115200)
            time.sleep(2)
            messagebox.showinfo("Notification", "Connected to "+self.optionVar.get()+"!")
            self.statusVar.set("   "+self.optionVar.get()+" is connected")
            self.statusConnect = True
            self.statusBar.configure(fg="#008000")
            self.buttonDisconnectPORT.configure(state=NORMAL)
            self.buttonConnectPORT.configure(state=DISABLED)
            self.buttonReloadListPORT.configure(state=DISABLED)
            self.buttonFirstPage.configure(state=DISABLED)
            self.buttonThirdPage.configure(state=DISABLED)
        except:
            messagebox.showerror("Error", "Can't connect, Please reconnect!")

    def disconnectToPORT(self):
        try:
            self.ser.close()
            self.ser = None
            messagebox.showinfo("Notification", "Disconnected to "+self.optionVar.get()+"!")
            self.optionVar.set("Not Selected")
            self.statusVar.set("   No connection")
            self.statusBar.configure(fg="#FF0000")
            self.statusConnect = False
            self.buttonConnectPORT.configure(state=NORMAL)
            self.buttonDisconnectPORT.configure(state=DISABLED)
            self.buttonReloadListPORT.configure(state=NORMAL)
            self.buttonFirstPage.configure(state=NORMAL)
            self.buttonThirdPage.configure(state=NORMAL)
        except:
            pass
        
    def reloadListPORT(self):
        self.ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            self.ports.append(port)
        self.optionVar.set("Not Selected")
        self.optionMenu["menu"].delete(0, "end")
        for port in self.ports:
            self.optionMenu["menu"].add_command(label=port, command=_setit(self.optionVar, port))

    def start(self):
        try:
            if int(self.entryStartV.get())<-825:
                messagebox.showerror("Error Potentiosat",
                                     "StartVoltage >= -825mV")
            elif int(self.entryEndV.get())>825:
                messagebox.showerror("Error Potentiosat",
                                     "StartVoltage <= 825mV")
            elif int(self.entryEndV.get())<int(self.entryStartV.get()):
                messagebox.showerror("Error Potentiosat",
                                     "EndVoltage > Start Voltage")
                # ok
            elif int(self.entryRT.get())>5 or int(self.entryRT.get())<1:
                messagebox.showerror("Error Potentiosat",
                                     "1 <= RepeatTimes <= 5")
            elif float(self.entryCoFreq.get())>=int(self.entryScanRate.get())/2:
                messagebox.showerror("Error Potentiosat",
                                     "1 <= Cutoff Frequence < Scan Rate/2")
            else:
                command = self.entryStartV.get()+"|"+self.entryEndV.get()+"_"+self.entryStep.get()+"?"+str(int(int(self.entryScanRate.get())/2))+"#"+self.entryRT.get()
                print(command)
                self.ser.write(command.encode(encoding = 'ascii', errors = 'strict'))
                self.statusPlot = True
                self.ax.set_xlim(int(self.entryStartV.get())-25, int(self.entryEndV.get())+25)
                self.ax.xaxis.set_ticks(np.arange(int(self.entryStartV.get()), int(self.entryEndV.get())+1, 100))
                self.buttonPause_Continue.configure(state=NORMAL)
                self.runAfter = self.run_after(10, self.runningPlot)
        except:
            messagebox.showerror("Error", "Please connect to the PORT to get started!")

    def pause(self):
        self.statusPlot = False
        self.buttonPause_Continue.configure(text="COUNTINUE", command=self.coutinue)
    
    def coutinue(self):
        self.statusPlot = True
        self.buttonPause_Continue.configure(text="PAUSE", command=self.pause)
        self.runAfter = self.run_after(10, self.runningPlot)

    def openFolder(self):
        try:
            if not os.path.exists("data"):
                os.mkdir("data")
            path = os.getcwd()
            os.startfile(path+"\data")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
            self.df.to_csv(patch+dt_str+".csv", index=False)
            self.fig.savefig(patch+dt_str+".png", dpi=300)
            self.fig_lowpass.savefig(patch+dt_str+"_lowpass"+".png", dpi=300)
            self.df = pd.DataFrame()
            messagebox.showinfo("Notification", "File is saved successfully")

    def resetData(self):
        self.canvas.get_tk_widget().destroy()
        self.frameDataTable.destroy()
        self.toolbar.destroy()
        self.entryConcentration.configure(text='None')

        self.idTreeView = []
        self.df = pd.DataFrame()
        self.statusPlot = False
        self.number = 0
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
       
        self.dataTable()
        self.createFigure()

        self.buttonSave.configure(state=DISABLED)
        self.buttonPause_Continue.configure(text="PAUSE",
                                            command=self.pause,
                                            state=DISABLED)

    def restart(self):
        self.resetData()

        self.statusConnect = False

        self.disconnectToPORT()
        
        self.reloadListPORT()

    def run_after(self, ms:int, command):
        run_after = self.after(ms, command)
        return run_after

    def cancel_after(self, id):
        self.after_cancel(id)
