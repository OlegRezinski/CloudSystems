import os
import time
import wx
import usingLib
import utils
import SearchHandler as se

class Example(wx.Frame):

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(880, 520))
        self.dict_en = {'Project folder': [self.projectScanEnable], 'Single search': [self.singleSearchEnable],
                   'Requirements file': [self.requirementsFileEnable]}

        self.location = os.getcwd()
        panel = wx.Panel(self)
        self.sb1 = wx.StaticBox(panel,5, label='Project scan', pos=(5,5), size=(650,80))

        self.lblsearchField = wx.StaticText(self.sb1, -1, "Project folder",pos=(10,20))
        self.textCtrlProjectPath = wx.TextCtrl(self.sb1, pos=(10, 40), size=(500,-1))

        self.btnLoadProjectFolder = wx.Button(self.sb1, -1, "Load folder", pos=(550, 40))
        self.btnLoadProjectFolder.Bind(wx.EVT_BUTTON, self.loadProjectFolder)

        self.sb2 = wx.StaticBox(panel,5, label='Single search', pos=(5,90), size=(650,80))

        self.lblLibrary = wx.StaticText(self.sb2, -1, "Library", pos=(5, 20))
        self.textCtrlLibrary = wx.TextCtrl(self.sb2, pos=(5, 45), size=(100, -1))

        self.lblVersion = wx.StaticText(self.sb2, -1, "Version", pos=(200, 20))
        self.textCtrlVersion = wx.TextCtrl(self.sb2, pos=(200, 45), size=(100, -1))

        self.sb3 = wx.StaticBox(panel,5, label='Scan requirements file', pos=(5,190), size=(650,80))

        self.lblReqFile = wx.StaticText(self.sb3, -1, "Requirements text File", pos=(5, 20))
        self.textReqFile = wx.TextCtrl(self.sb3, pos=(5, 45), size=(500, -1))

        self.btnLoadTextFile = wx.Button(self.sb3, -1, "Load file", pos=(550,45))
        self.btnLoadTextFile.Bind(wx.EVT_BUTTON, self.loadReqFile)

        self.sb4 = wx.StaticBox(panel,5, label='Risk assessment', pos=(5,290), size=(650,100))

        self.lblReqFile = wx.StaticText(self.sb4 , -1, "Risk scale", pos=(5, 20))
        self.gaugeRiskScale = wx.Gauge(self.sb4, range=100, pos=(5,45),size=(500,30))

        self.lblReqFile = wx.StaticText(self.sb4 , -1, "Risk score:", pos=(510, 50))
        self.textCtrlRiskScore = wx.TextCtrl(self.sb4 , pos=(580, 45), size=(40,30))
        self.textCtrlRiskScore.Disable()

        self.btn_run = wx.Button(panel, -1, "Execute", pos=(300, 410), size=(300, 30))
        self.btn_run.Bind(wx.EVT_BUTTON, self.runBtnClicked)

        lblList = ['Project folder', 'Single search', 'Requirements file']
        self.rbox = wx.RadioBox(panel, label='Scan options', pos=(700, 10), choices=lblList,
                                majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        self.projectScanEnable(True)
        self.singleSearchEnable(False)
        self.requirementsFileEnable(False)



    def runBtnClicked(self, event):
        selection = self.rbox.GetStringSelection()
        self.runSelection(selection)

    def loadReqFile(self, event):
        with wx.FileDialog(self, "Load requirements file", wildcard="text files (*.txt)|*.txt", style=wx.FD_OPEN) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            self.textReqFile.SetValue(pathname)

    def loadProjectFolder(self, event):
        dlg = wx.DirDialog(self, message="Choose project folder")
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetPath()

        dlg.Destroy()
        self.textCtrlProjectPath.SetValue(dirname)

    def onRadioBox(self, e):
        selection = self.rbox.GetStringSelection()
        self.disableNotSelected(selection)

    def disableNotSelected(self, selection):
        for key in self.dict_en:
            if key == selection:
                self.dict_en[key][0](True)
            else:
                self.dict_en[key][0](False)

        self.Refresh()
        return

    def projectScanEnable(self,en):
        self.textCtrlProjectPath.Enable(en)
        self.btnLoadProjectFolder.Enable(en)

    def singleSearchEnable(self,en):
        self.textCtrlLibrary.Enable(en)
        self.textCtrlVersion.Enable(en)

    def requirementsFileEnable(self, en):
        self.textReqFile.Enable(en)
        print(self.textReqFile.GetValue())
        self.btnLoadTextFile.Enable(en)

    def runSingleSearch(self):
        # self.textCtrlRiskScore.SetValue(' ')
        # self.gaugeRiskScale.SetValue(0)
        # self.Refresh()
        self.resetResultFeatures()
        keyWord = self.textCtrlLibrary.GetValue()
        ver = self.textCtrlVersion.GetValue()
        # score,err_msg = usingLib.main(keyWord, ver)
        df_result, err_msg = se.singleSearch(keyWord, ver)
        if err_msg:
            wx.MessageBox(err_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
            return
        if not df_result.empty:
            score = df_result['Score'].max()
            # self.gaugeRiskScale.SetValue(round(score*10))
            # self.textCtrlRiskScore.SetValue(str(score))
            self.setResultFeatures(score)



    def runReqFileSearch(self,filePath=None):
        self.resetResultFeatures()
        if not filePath:
            filePath = self.textReqFile.GetValue()
        if not filePath:
            wx.MessageBox('file path cannot remain empty', 'Info', wx.OK | wx.ICON_INFORMATION)
            return

        df_res, err_msg = se.runReqFileSearch(filePath)

        if not df_res.empty:
            maxScore = df_res['Score'].max()
            self.setResultFeatures(maxScore)
            outpath = os.path.join(self.location,'results.csv')
            df_res.to_csv(outpath)


    def runProjectFolderScan(self):
        self.resetResultFeatures()
        proj_folder = self.textCtrlProjectPath.GetValue()
        if not os.path.exists(proj_folder):
            wx.MessageBox(f'{proj_folder} path does not exist', 'Info', wx.OK | wx.ICON_INFORMATION)
            return
        os.chdir(proj_folder)
        os.system("pip freeze > req.txt")
        time.sleep(3)
        file_path = os.path.join(proj_folder, "req.txt")
        if not os.path.exists(file_path):
            wx.MessageBox(f'{file_path} was not created', 'Info', wx.OK | wx.ICON_INFORMATION)
            return

        # df_res, err_msg = se.runReqFileSearch(file_path)
        #
        # if not df_res.empty:
        #     maxScore = df_res['Score'].max()
        #     self.setResultFeatures(maxScore)
        #     outpath = os.path.join(self.location, 'results.csv')
        #     df_res.to_csv(outpath)

        self.runReqFileSearch(file_path)

    def runSelection(self,selection):

        if selection == 'Project folder':
            self.runProjectFolderScan()
            return
        if selection == 'Single search':
            self.runSingleSearch()
            return
        if selection == 'Requirements file':
            self.runReqFileSearch()


    def resetResultFeatures(self):
        self.textCtrlRiskScore.SetValue('')
        self.gaugeRiskScale.SetValue(0)
        self.Refresh()

    def setResultFeatures(self, score):
        self.textCtrlRiskScore.SetValue(str(score))
        self.gaugeRiskScale.SetValue(round(score*10))
        self.Refresh()

def main():

    app = wx.App()
    ex = Example(None, title='Project Name')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()