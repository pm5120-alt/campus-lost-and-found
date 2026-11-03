import tkinter as tk
from tkinter import messagebox
import database
from ui.welcome import Welcome
from ui.auth import Auth
from ui.dashboard import Dashboard
from ui import theme as T

class CampusApp(tk.Tk):
    def __init__(self):
        super().__init__();self.title('Campus Lost & Found  |  SRM KTR');self.configure(bg=T.BG);self.geometry('1360x850');self.minsize(1040,700);self._screen=None
        try:self.state('zoomed')
        except tk.TclError:pass
        database.setup_database();self.show_welcome()
        self.protocol('WM_DELETE_WINDOW',self.close)
    def replace(self,screen):
        if self._screen:
            try:self._screen.destroy()
            except tk.TclError:pass
        self._screen=screen;screen.pack(fill='both',expand=True)
    def show_welcome(self):self.replace(Welcome(self,self.show_auth))
    def show_auth(self):self.replace(Auth(self,self.show_dashboard,self.show_welcome))
    def show_dashboard(self,user):self.replace(Dashboard(self,user,self.show_auth))
    def close(self):
        if self._screen:
            try:self._screen.destroy()
            except tk.TclError:pass
        self.destroy()

def main():
    try:CampusApp().mainloop()
    except Exception as e:
        root=tk.Tk();root.withdraw();messagebox.showerror('Startup error',f'Campus Lost & Found could not start.\n\n{e}');root.destroy();raise

if __name__=='__main__':main()
