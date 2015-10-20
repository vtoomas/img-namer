from Tkinter import *
from Rename_JPEG import *
import tkFileDialog, os, tkMessageBox

class Application(Frame):
    def browse_file(self):
        file_path = tkFileDialog.askopenfilenames()
        for p in file_path:
            self.file_names.append(self.fullpath_to_list(p))

        self.display_selected(self.patBox.get())

    def browse_dir(self):
        dir_path = tkFileDialog.askdirectory()
        files = explore_dir(dir_path)
        for p in files:
            self.file_names.append(self.fullpath_to_list(p))
        
        self.display_selected(self.patBox.get())

    def get_filename_full(self, _index):
        return os.path.join(self.file_names[_index][0], self.file_names[_index][1]) + self.file_names[_index][2]

    def fullpath_to_list(self, fullpath):
        fdir, fn = os.path.split(fullpath)
        fn, ext = os.path.splitext(fn)
        fullpath = os.path.join(fdir, fn, ext)
        return [fdir, fn, ext]

    def display_selected(self, P):
        if len(self.file_names) == 0:
            self.patResult.set("No files selected")
        else:
            try:
                name_prev = new_name(self.get_filename_full(0), P)
                prev_list = self.fullpath_to_list(name_prev)
                self.patResult.set(prev_list[1] + prev_list[2])
            except Exception, e:
                print e
                self.patResult.set("Error parsing file")

        return True

    def run_Rename(self):
        for i in xrange(len(self.file_names)):
            rename_file(self.get_filename_full(i), self.patBox.get())
        tkMessageBox.showinfo('Done', 'Files have been renamed successfully. ')
        self.file_names = []
        self.display_selected(self.patBox.get())

    def createWidgets(self):
        self.tcont = Frame(root)
        self.tcont.pack(side = TOP)
        self.mcont = Frame(root)
        self.mcont.pack()
        self.bcont = Frame(root)
        self.bcont.pack(side = BOTTOM)        
        
        self.selectInfo = Label(self.tcont)
        self.selectInfo["text"] = "Select images by:"
        self.selectInfo.pack(side = LEFT)

        self.dirBtn = Button(self.tcont)
        self.dirBtn["text"] = "Folder"
        self.dirBtn["command"] =  self.browse_dir
        self.dirBtn.pack({"side": "right"})

        self.fileBtn = Button(self.tcont)
        self.fileBtn["text"] = "File",
        self.fileBtn["command"] = self.browse_file
        self.fileBtn.pack({"side": "right"})

        self.patInfo = Label(self.mcont)
        self.patInfo["text"] = "Pattern: "
        self.patInfo.pack(side = LEFT)

        vcmd = (self.register(self.display_selected), '%P')
        self.patBox = Entry(self.mcont, textvariable = self.patVar, exportselection = 0, validate = "all", validatecommand = vcmd)
        self.patBox.pack()

        self.resultLabel = Label(self.bcont, textvariable = self.patResult)
        self.resultLabel.pack(side = TOP)

        self.runBtn = Button(self.bcont)
        self.runBtn["text"] = "Rename"
        self.runBtn["command"] = self.run_Rename
        self.runBtn.pack()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.file_names = [] # as [[path, filename, extension], [...]]
        self.patVar = StringVar()
        self.patVar.set("yyyy-MM-dd-hhmmss.MODEL")
        self.patResult = StringVar()
        self.patResult.set("No files selected")

        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
