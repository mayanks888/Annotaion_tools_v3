import tkSimpleDialog
# from Tkinter import messagebox
# #
# ?
#
from Tkinter import *
from tkMessageBox import *


def callback():
    tkMessageBox.showinfo("Alert Message", "This is just a alert message!")
    number = tkSimpleDialog.askinteger("Integer", "Enter your Image_id")
    print(" id id ", number)
    root.destroy()
    # return number
    # root.quit()


def answer():
    showerror("Answer", "Sorry, no answer available")
    # root.quit()
    return 1


#
# result = askcolor(color="#6A9662", title="Bernd's Colour Chooser")
# print result
root = Tk()
root.geometry("+1750+400")
Button(root, text='Give custom ID', fg="darkgreen", command=callback).pack(side=LEFT, padx=10)
Button(text='Set default', command=root.quit, fg="red").pack(side=LEFT, padx=10)
# print (a)
mainloop()
