import tkinter as tk
from tkinter import ttk
from ui import theme as T

def label(master,text='',**kw): return tk.Label(master,text=text,bg=kw.pop('bg',T.PANEL),fg=kw.pop('fg',T.TEXT),font=kw.pop('font',(T.FONT,10)),**kw)
def button(master,text,command,kind='primary',**kw):
    bg={'primary':T.CYAN,'secondary':T.PANEL2,'danger':'#4b2432','success':'#12382f'}[kind];fg={'primary':BG if False else '#04111d','secondary':T.TEXT,'danger':'#ff9baa','success':T.GREEN}[kind]
    b=tk.Button(master,text=text,command=command,bg=bg,fg=fg,activebackground=T.BLUE if kind=='primary' else T.LINE,activeforeground=T.TEXT,relief='flat',bd=0,cursor='hand2',font=(T.FONT,10,'bold'),padx=16,pady=10,**kw)
    b.bind('<Enter>',lambda e:b.configure(bg=T.BLUE if kind=='primary' else T.LINE));b.bind('<Leave>',lambda e:b.configure(bg=bg));return b
def card(master,**kw): return tk.Frame(master,bg=T.PANEL,highlightbackground=T.LINE,highlightthickness=1,**kw)
def entry(master,show=None,**kw):
    return tk.Entry(master,bg='#091625',fg=T.TEXT,insertbackground=T.CYAN,relief='flat',highlightthickness=1,highlightbackground=T.LINE,highlightcolor=T.CYAN,font=(T.FONT,11),show=show,**kw)
def set_status(var,message): var.set(message)
