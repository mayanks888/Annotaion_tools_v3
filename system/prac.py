import Tkinter
import tkMessageBox

top = Tkinter.Tk()


def helloCallBack():
    tkMessageBox.showinfo("Hello Python", "Hello World")


B = Tkinter.Button(top, text="Hello", command=helloCallBack)
B.grid(row=4, column=2, sticky='we')
# B.pack(side=LEFT, padx=5, pady=5)
A = Tkinter.Button(top, text="Other", command=helloCallBack)

B.pack()
A.pack()

################################3333
# self.btnDel = Button(self.frame, text='Delete', command=self.delBBox)
# self.btnDel.grid(row=4, column=2, sticky=W + E + N)
# self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
# self.btnClear.grid(row=5, column=2, sticky=W + E + N)
#########################################
top.mainloop()
