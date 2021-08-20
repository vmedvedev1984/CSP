from PyQt5 import QtWidgets, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QCheckBox
#from PyQt5.QtWidgets import QTableWidgetItem
#from PyQt5.QtGui import QPen, QColor, QImage, QPixmap, QPainter
#from PyQt5.QtCore import Qt, QTime, QCoreApplication, QEventLoop, QPointF
from openpyxl import Workbook, load_workbook
from docxtpl import DocxTemplate
import io, os, time, fnmatch, csv, datetime, json

class popupwin():
    def __init__(self):
        self.text = ""
        self.title = ""
    
    def win(self, text, title):
        infoBox = QMessageBox()
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText(text)
        infoBox.setWindowTitle(title)
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.exec_()

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi("MainWindow.ui", self)
        #загрузка конфигурационного файла 
        self.fastalist = []
        with open('config.txt') as json_file:  
            self.data = json.load(json_file)
        #self.label.setText("NewText")
        self.pushButton_6.clicked.connect(self.prepFa)
        self.pushButton_5.clicked.connect(self.stat)
        self.comboBox.addItems(["40nmol", "200nmol", "1umol"])
        self.comboBox_2.addItems(["ETT", "DCI"])
        self.pushButton.clicked.connect(self.postprocXLS)
        self.pushButton_2.clicked.connect(self.postXLSedit)
        #self.pushButton.clicked.connect(self.stat)
        self.tabWidget.setCurrentIndex(0)

    def popupwin(self, text, title):
        infoBox = QMessageBox()
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText(text)
        infoBox.setWindowTitle(title)
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.exec_()        

    def stat(self):
        self.totemplate()
        wb = Workbook()
        #wb = openpyxl.load_workbook(filename = './template.xlsx')
        sheet = wb.active
        wb_first_row = ['Name', 'Sequence', 'Lenght', 'M.W.', 'Coef.Ext.', 'GC%', 'ug/OD250']
        for tab_colm in range(len(wb_first_row)):
            sheet.cell(row=1, column=tab_colm + 1).value = wb_first_row[tab_colm]
        for tab_row in range(2, len(self.fastalist) + 2):
            sheet.cell(row = tab_row, column = 1).value = self.tableWidget.item(tab_row - 2, 0).text()
            sheet.cell(row = tab_row, column = 2).value = self.tableWidget.item(tab_row - 2, 1).text()
            sheet.cell(row = tab_row, column = 3).value = int(self.tableWidget.item(tab_row - 2, 2).text())
            sheet.cell(row = tab_row, column = 4).value = self.tableWidget.item(tab_row - 2, 3).text().replace(".", ",")
            sheet.cell(row = tab_row, column = 5).value = self.tableWidget.item(tab_row - 2, 4).text()
            sheet.cell(row = tab_row, column = 6).value = self.tableWidget.item(tab_row - 2, 5).text().replace(".", ",")
            sheet.cell(row = tab_row, column = 7).value = self.tableWidget.item(tab_row - 2, 6).text().replace(".", ",")
        wb.save('./synthes/synthesis ' + str(datetime.date.today()) + '.xlsx')
        
        
    
    def totemplate(self):
        Mon_All = int(self.label_A_val.text())+int(self.label_C_val.text())+int(self.label_G_val.text())+int(self.label_T_val.text())
        context = { 'dA' : str(round((((float(self.label_A_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol'])*(self.data['config'][1]['Amd']/self.data['config'][1]['MeCN'])),5)) + ' г',
                    'MeCN_dA' : str(round(((float(self.label_A_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol']),4)) + ' мл',
                    'dC' : str(round((((float(self.label_C_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol'])*(self.data['config'][1]['Amd']/self.data['config'][1]['MeCN'])),5)) + ' г',
                    'MeCN_dC' : str(round(((float(self.label_C_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol']),4)) + ' мл',
                    'dG' : str(round((((float(self.label_G_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol'])*(self.data['config'][1]['Amd']/self.data['config'][1]['MeCN'])),5)) + ' г',
                    'MeCN_dG' : str(round(((float(self.label_G_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol']),4)) + ' мл',
                    'dT' : str(round((((float(self.label_T_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol'])*(self.data['config'][1]['Amd']/self.data['config'][1]['MeCN'])),5)) + ' г',
                    'MeCN_dT' : str(round(((float(self.label_T_val.text())*self.data['config'][1]['VolOneBase'])+self.data['config'][1]['DeadVol']),4)) + ' мл',
                    'THF_Ox' : str(round(float(((Mon_All*self.data['config'][2]['VolOneBase'])+self.data['config'][2]['DeadVol'])*((self.data['config'][2]['THF'])/(self.data['config'][2]['THF']+self.data['config'][2]['Py']+self.data['config'][2]['H2O']))),5)) + ' мл',
                    'Py_Ox' : str(round(float(((Mon_All*self.data['config'][2]['VolOneBase'])+self.data['config'][2]['DeadVol'])*((self.data['config'][2]['Py'])/(self.data['config'][2]['THF']+self.data['config'][2]['Py']+self.data['config'][2]['H2O']))),5)) + ' мл',
                    'H2O_Ox' : str(round(float(((Mon_All*self.data['config'][2]['VolOneBase'])+self.data['config'][2]['DeadVol'])*((self.data['config'][2]['H2O'])/(self.data['config'][2]['THF']+self.data['config'][2]['Py']+self.data['config'][2]['H2O']))),5)) + ' мл',
                    'I2_Ox' : str(round(float(((Mon_All*self.data['config'][2]['VolOneBase'])+self.data['config'][2]['DeadVol'])*((self.data['config'][2]['I2'])/(self.data['config'][2]['THF']+self.data['config'][2]['Py']+self.data['config'][2]['H2O']))),5)) + ' г',
                    'V_Ox' : str(round(float((Mon_All*self.data['config'][2]['VolOneBase'])+self.data['config'][2]['DeadVol']),5)) + ' мл',
                    'MeCN_Act' : str(round(float((Mon_All*self.data['config'][3]['VolOneBase'])+self.data['config'][3]['DeadVol']),5)) + ' мл',
                    'TET_Act' : str(round(float(((Mon_All*self.data['config'][3]['VolOneBase'])+self.data['config'][3]['DeadVol'])*(self.data['config'][3]['TET']/self.data['config'][3]['MeCN'])),5)) + ' г',
                    'DCE_Dbl' : str(round(float(((Mon_All*self.data['config'][4]['VolOneBase'])+self.data['config'][4]['DeadVol'])*(self.data['config'][4]['DCE']/(self.data['config'][4]['DCE']+self.data['config'][4]['DCA']))),5)) + ' мл',
                    'DCA_Dbl' : str(round(float(((Mon_All*self.data['config'][4]['VolOneBase'])+self.data['config'][4]['DeadVol'])*(self.data['config'][4]['DCA']/(self.data['config'][4]['DCE']+self.data['config'][4]['DCA']))),5)) + ' мл',
                    'V_Dbl' : str(round(float((Mon_All*self.data['config'][4]['VolOneBase'])+self.data['config'][4]['DeadVol']),5)) + ' мл',
                    'THF_CPA' : str(round(float(((Mon_All*self.data['config'][5]['VolOneBase'])+self.data['config'][5]['DeadVol'])*(self.data['config'][5]['THF']/(self.data['config'][5]['THF']+self.data['config'][5]['Anhydride']+self.data['config'][5]['Py']))),5)) + ' мл',
                    'ANH_CPA' : str(round(float(((Mon_All*self.data['config'][5]['VolOneBase'])+self.data['config'][5]['DeadVol'])*(self.data['config'][5]['Anhydride']/(self.data['config'][5]['THF']+self.data['config'][5]['Anhydride']+self.data['config'][5]['Py']))),5)) + ' мл',
                    'Py_CPA' : str(round(float(((Mon_All*self.data['config'][5]['VolOneBase'])+self.data['config'][5]['DeadVol'])*(self.data['config'][5]['Py']/(self.data['config'][5]['THF']+self.data['config'][5]['Anhydride']+self.data['config'][5]['Py']))),5)) + ' мл',
                    'V_CPA' : str(round(float((Mon_All*self.data['config'][5]['VolOneBase'])+self.data['config'][5]['DeadVol']),5)) + ' мл',
                    'THF_CPB' : str(round(float(((Mon_All*self.data['config'][6]['VolOneBase'])+self.data['config'][6]['DeadVol'])*(self.data['config'][6]['THF']/(self.data['config'][6]['THF']+self.data['config'][6]['MeIm']))),5)) + ' мл',
                    'MeIm_CPB' : str(round(float(((Mon_All*self.data['config'][6]['VolOneBase'])+self.data['config'][6]['DeadVol'])*(self.data['config'][6]['MeIm']/(self.data['config'][6]['THF']+self.data['config'][6]['MeIm']))),5)) + ' мл',
                    'V_CPB' : str(round(float((Mon_All*self.data['config'][6]['VolOneBase'])+self.data['config'][6]['DeadVol']),5)) + ' мл',
                    'DCI_Act' : str(round(float(((Mon_All*self.data['config'][7]['VolOneBase'])+self.data['config'][7]['DeadVol'])*(self.data['config'][7]['DCI']/self.data['config'][7]['MeCN'])),5)) + ' г',
                    'TET_Act_1' : True if self.comboBox_2.currentText() == 'ETT' else False,
                    'DCI_Act_1' : True if self.comboBox_2.currentText() == 'DCI' else False,
                    eval('olig_name_' + str(olig_num) : str(self.tableWidget.item(olig_num, 0).text() if self.tableWidget.item(olig_num, 0) != None else '')) for olig_num in range(12)),
                    'olig_seq_1' : str(self.tableWidget.item(0, 1).text() if self.tableWidget.item(0, 1) != None else ''),
                    'olig_seq_2' : str(self.tableWidget.item(1, 1).text() if self.tableWidget.item(1, 1) != None else ''),
                    'olig_seq_3' : str(self.tableWidget.item(2, 1).text() if self.tableWidget.item(2, 1) != None else ''),
                    'olig_seq_4' : str(self.tableWidget.item(3, 1).text() if self.tableWidget.item(3, 1) != None else ''),
                    'olig_seq_5' : str(self.tableWidget.item(4, 1).text() if self.tableWidget.item(4, 1) != None else ''),
                    'olig_seq_6' : str(self.tableWidget.item(5, 1).text() if self.tableWidget.item(5, 1) != None else ''),
                    'olig_seq_7' : str(self.tableWidget.item(6, 1).text() if self.tableWidget.item(6, 1) != None else ''),
                    'olig_seq_8' : str(self.tableWidget.item(7, 1).text() if self.tableWidget.item(7, 1) != None else ''),
                    'olig_seq_9' : str(self.tableWidget.item(8, 1).text() if self.tableWidget.item(8, 1) != None else ''),
                    'olig_seq_10' : str(self.tableWidget.item(9, 1).text() if self.tableWidget.item(9, 1) != None else ''),
                    'olig_seq_11' : str(self.tableWidget.item(10, 1).text() if self.tableWidget.item(10, 1) != None else ''),
                    'olig_seq_12' : str(self.tableWidget.item(11, 1).text() if self.tableWidget.item(11, 1) != None else ''),
                    'ol_n_1' : str(self.tableWidget.item(0, 2).text() if self.tableWidget.item(0, 2) != None else ''),
                    'ol_n_2' : str(self.tableWidget.item(1, 2).text() if self.tableWidget.item(1, 2) != None else ''),
                    'ol_n_3' : str(self.tableWidget.item(2, 2).text() if self.tableWidget.item(2, 2) != None else ''),
                    'ol_n_4' : str(self.tableWidget.item(3, 2).text() if self.tableWidget.item(3, 2) != None else ''),
                    'ol_n_5' : str(self.tableWidget.item(4, 2).text() if self.tableWidget.item(4, 2) != None else ''),
                    'ol_n_6' : str(self.tableWidget.item(5, 2).text() if self.tableWidget.item(5, 2) != None else ''),
                    'ol_n_7' : str(self.tableWidget.item(6, 2).text() if self.tableWidget.item(6, 2) != None else ''),
                    'ol_n_8' : str(self.tableWidget.item(7, 2).text() if self.tableWidget.item(7, 2) != None else ''),
                    'ol_n_9' : str(self.tableWidget.item(8, 2).text() if self.tableWidget.item(8, 2) != None else ''),
                    'ol_n_10' : str(self.tableWidget.item(9, 2).text() if self.tableWidget.item(9, 2) != None else ''),
                    'ol_n_11' : str(self.tableWidget.item(10, 2).text() if self.tableWidget.item(10, 2) != None else ''),
                    'ol_n_12' : str(self.tableWidget.item(11, 2).text() if self.tableWidget.item(11, 2) != None else ''),
                    'month' : str(datetime.date.today()).split('-')[1],
                    'day' : str(datetime.date.today()).split('-')[2],
        }
        doc = DocxTemplate("protocol_template.docx")
        doc.render(context)
        doc.save("./protocols/Протокол синтеза олигонуклеотидов " + str(datetime.date.today()) + ".docx")
        # всплывающие окно информации о сборке файла протокола синтеза
        self.popupwin("Протокол синтеза готов", "Информация")
        #состояние CheckBox-ов DMT-On
        '''for dmt_check in range(len(self.fastalist)):
            print(int(self.tableWidget.cellWidget(dmt_check, 7).checkState()))
            
            'olig_name_1' : str(self.tableWidget.item(0, 0).text() if self.tableWidget.item(0, 0) != None else ''),
                    'olig_name_2' : str(self.tableWidget.item(1, 0).text() if self.tableWidget.item(1, 0) != None else ''),
                    'olig_name_3' : str(self.tableWidget.item(2, 0).text() if self.tableWidget.item(2, 0) != None else ''),
                    'olig_name_4' : str(self.tableWidget.item(3, 0).text() if self.tableWidget.item(3, 0) != None else ''),
                    'olig_name_5' : str(self.tableWidget.item(4, 0).text() if self.tableWidget.item(4, 0) != None else ''),
                    'olig_name_6' : str(self.tableWidget.item(5, 0).text() if self.tableWidget.item(5, 0) != None else ''),
                    'olig_name_7' : str(self.tableWidget.item(6, 0).text() if self.tableWidget.item(6, 0) != None else ''),
                    'olig_name_8' : str(self.tableWidget.item(7, 0).text() if self.tableWidget.item(7, 0) != None else ''),
                    'olig_name_9' : str(self.tableWidget.item(8, 0).text() if self.tableWidget.item(8, 0) != None else ''),
                    'olig_name_10' : str(self.tableWidget.item(9, 0).text() if self.tableWidget.item(9, 0) != None else ''),
                    'olig_name_11' : str(self.tableWidget.item(10, 0).text() if self.tableWidget.item(10, 0) != None else ''),
                    'olig_name_12' : str(self.tableWidget.item(11, 0).text() if self.tableWidget.item(11, 0) != None else ''),
            
            '''
            


    def postprocXLS(self):
        self.XLSdir = QFileDialog.getOpenFileName(None, 'Open File', './synthes/', "Excel Files (*.xlsx)")
        if self.XLSdir[0][-4:] == 'xlsx':
            self.textEdit_2.setText(self.XLSdir[0])
            wbCSV = load_workbook(filename = self.XLSdir[0])
            XLSopen = []
            sheet_ranges = wbCSV['Sheet']
            lensheet_range = 0
            while(lensheet_range < len(sheet_ranges['A'])):
                XLSopen.append(sheet_ranges['A' + str(lensheet_range + 1)].value)
                XLSopen.append(sheet_ranges['B' + str(lensheet_range + 1)].value)
                lensheet_range += 1
        else:
            return 0
        print(XLSopen[2::2])
        for row in range(len(XLSopen[2::2])):
            self.tableWidget_2.insertRow(row)
            self.tableWidget_2.setItem(row, 0, QtWidgets.QTableWidgetItem(XLSopen[2*row + 2]))
            self.tableWidget_2.setItem(row, 1, QtWidgets.QTableWidgetItem(XLSopen[2*row + 3]))
        self.tableWidget_2.resizeColumnsToContents()
        

    def postXLSedit(self):
        wbCSV = load_workbook(filename = self.XLSdir[0])
        sheet_ranges = wbCSV['Sheet']
        sheet_ranges.cell(row = 1, column = 8).value = "C, ng/ul"
        sheet_ranges.cell(row = 1, column = 9).value = "Add Water, ul"    
        for tab_r in range(len(sheet_ranges['A'])-1):
            sheet_ranges.cell(row = tab_r + 2, column = 8).value = self.tableWidget_2.item(tab_r, 2).text()
            sheet_ranges.cell(row = tab_r + 2, column = 9).value = (((float(self.tableWidget_2.item(tab_r, 2).text().replace(",", "."))) / float(sheet_ranges.cell(row = tab_r + 2, column = 4).value.replace(",", ".")))*1000)-100
            self.tableWidget_2.setItem(tab_r, 3, QtWidgets.QTableWidgetItem(str(sheet_ranges.cell(row = tab_r + 2, column = 9).value)))
        wbCSV.save(self.XLSdir[0])
        self.popupwin("Рабочий файл дополнен", "Информация")


    def prepFa(self):
        self.fastadir = QFileDialog.getOpenFileName(None, 'Open File', './', "Fasta (*.fa *.fasta);;CSV Files (*.csv)")
        self.textEdit.setText(self.fastadir[0])
        if self.fastadir[0][-2:] == 'fa' or self.fastadir[0][-5:] == 'fasta':
            fastaopen = io.open(self.fastadir[0], mode='r').read().split()
            #print(fastaopen)
        elif self.fastadir[0][-3:] == 'csv':
            fastaopen = []
            f = open(self.fastadir[0], newline = '') 
            with f as csvfile:
                readCSV = csv.reader(csvfile, delimiter=';')
                for row in readCSV:
                    fastaopen.append('>' + row[0])
                    fastaopen.append(row[1])
            f.close()
        else:
            return 0
        i=0
        self.fastalist = []
        fastalistname = []
        coefex = []
        MWlist = []
        GClist =[]
        dA = 0
        dC = 0
        dG = 0
        dT = 0
        lenght_item = []
        while i<len(fastaopen):
            if fastaopen[i][0] == '>':
                fastalistname.append(fastaopen[i])
                i=i+1
            else:
                self.fastalist.append(fastaopen[i])
                #-------Coef.Ext---------
                item_seq_ext = 0
                MW = 0
                GC = 0
                A = 0
                C = 0
                G = 0
                T = 0
                leight = 0
                for j in range(len(fastaopen[i])-1):
                    if fastaopen[i][j] == "A" :
                        dA = dA + 1 
                        A = A + 1
                        MW = MW + 251.2
                        if fastaopen[i][j+1] == "A":
                            item_seq_ext = item_seq_ext + 27400 - 15400  #ex(AA)-ex(A)
                        elif fastaopen[i][j+1] == "C" :
                            item_seq_ext = item_seq_ext + 21200 - 7400 #ex(AC)-ex(A)
                        elif fastaopen[i][j+1] == "G":
                            item_seq_ext = item_seq_ext + 25000 - 11500 #ex(AG)-ex(A)
                        elif fastaopen[i][j+1] == "T":
                            item_seq_ext = item_seq_ext + 22800 - 8700 #ex(AT)-ex(A)
                    if fastaopen[i][j] == "C" :
                        dC = dC +1
                        C = C + 1
                        MW = MW + 227.2
                        GC = GC + 1
                        if fastaopen[i][j+1] == "A":
                            item_seq_ext = item_seq_ext + 21200 - 15400 #ex(CA)-ex(A)
                        elif fastaopen[i][j+1] == "C" :
                            item_seq_ext = item_seq_ext + 14600 - 7400 #ex(CC)-ex(A)
                        elif fastaopen[i][j+1] == "G":
                            item_seq_ext = item_seq_ext + 18000 - 11500 #ex(CG)-ex(A)
                        elif fastaopen[i][j+1] == "T":
                            item_seq_ext = item_seq_ext + 15200 - 8700 #ex(CT)-ex(A)
                    if fastaopen[i][j] == "G" :
                        dG = dG +1
                        G = G + 1
                        MW = MW + 267.2
                        GC = GC + 1
                        if fastaopen[i][j+1] == "A" :
                            item_seq_ext = item_seq_ext + 25200 - 15400 #ex(GA)-ex(A)
                        elif fastaopen[i][j+1] == "C" :
                            item_seq_ext = item_seq_ext + 17600 - 7400 #ex(GC)-ex(A)
                        elif fastaopen[i][j+1] == "G":
                            item_seq_ext = item_seq_ext + 21600 - 11500 #ex(GG)-ex(A)
                        elif fastaopen[i][j+1] == "T":
                            item_seq_ext = item_seq_ext + 20000 - 8700 #ex(GT)-ex(A)
                    if fastaopen[i][j] == "T" :
                        dT = dT + 1
                        T = T + 1
                        MW = MW + 242.2
                        if fastaopen[i][j+1] == "A" :
                            item_seq_ext = item_seq_ext + 23400 - 15400 #ex(GA)-ex(A)
                        elif fastaopen[i][j+1] == "C" :
                            item_seq_ext = item_seq_ext + 16200 - 7400 #ex(GC)-ex(A)
                        elif fastaopen[i][j+1] == "G":
                            item_seq_ext = item_seq_ext + 19000 - 11500 #ex(GG)-ex(A)
                        elif fastaopen[i][j+1] == "T":
                            item_seq_ext = item_seq_ext + 16800 - 8700 #ex(GT)-ex(A)
                if fastaopen[i][-1] == "A":
                    dA = dA +1
                    A = A + 1
                    MW = MW + 251.2
                    item_seq_ext = item_seq_ext + 15400
                elif fastaopen[i][-1] == "C":
                    dC = dC + 1
                    C = C + 1
                    MW = MW +227.2
                    GC = GC + 1
                    item_seq_ext = item_seq_ext + 7400
                elif fastaopen[i][-1] == "G":
                    dG = dG +1
                    G = G + 1
                    MW = MW + 267
                    GC = GC + 1
                    item_seq_ext = item_seq_ext + 11500
                elif fastaopen[i][-1] == "T":
                    dT = dT + 1
                    T = T + 1
                    MW = MW + 242.2
                    item_seq_ext = item_seq_ext + 8700
                MW = MW + (len(fastaopen[i])-1)*62.05        #фосфатный остов
                GC = (GC / len(fastaopen[i]))*100
                coefex.append(item_seq_ext)
                MWlist.append(MW)
                GClist.append(GC)
                leight = A + T + C + G
                lenght_item.append(leight)
                i=i+1

        for row in range(len(self.fastalist)):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(fastalistname[row][1:]))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(self.fastalist[row]))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(lenght_item[row])))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(format(MWlist[row], '.2f'))))
            self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(str(coefex[row])))
            self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(str(format(GClist[row], '.2f'))))
            self.tableWidget.setItem(row, 6, QtWidgets.QTableWidgetItem(str(format(((MWlist[row]/coefex[row])*1000), '.2f'))))
            #self.tableWidget.cellWidget(row, 7).checkState()
            self.tableWidget.setCellWidget(row,7, QCheckBox())
            #self.tableWidget.setItem(row, 7, QtWidgets.QTableWidgetItem(QCheckBox('Show title', self)))
            self.label_A_val.setText(str(dA))
            self.label_C_val.setText(str(dC))
            self.label_G_val.setText(str(dG))
            self.label_T_val.setText(str(dT))
        
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())