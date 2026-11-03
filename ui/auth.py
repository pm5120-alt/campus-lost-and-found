import tkinter as tk
from tkinter import messagebox, simpledialog
import database
from validators import validate_password
from ui import theme as T
from ui.common import button,card,entry,label

class Auth(tk.Frame):
    def __init__(self,master,on_login,on_back):
        super().__init__(master,bg=T.BG);self.on_login=on_login;self.on_back=on_back;self.mode='login';self._draw()
    def _draw(self):
        for w in self.winfo_children():w.destroy()
        shell=card(self);shell.place(relx=.5,rely=.5,anchor='center',width=480,height=600)
        label(shell,text='CAMPUS  /  IDENTITY',fg=T.CYAN,font=('Segoe UI',9,'bold')).pack(anchor='w',padx=38,pady=(34,4))
        label(shell,text='Welcome back' if self.mode=='login' else 'Create your student account',font=('Segoe UI',23,'bold')).pack(anchor='w',padx=38)
        label(shell,text='Use your campus identity to continue.',fg=T.MUTED).pack(anchor='w',padx=38,pady=(5,20))
        self.fields={}
        for key,title,secret in [('username','Username',False),('password','Password',True)]+([('confirm','Confirm password',True)] if self.mode=='register' else []):
            label(shell,text=title,fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',padx=38,pady=(8,5))
            e=entry(shell,show='●' if secret else None);e.pack(fill='x',padx=38,ipady=11);self.fields[key]=e
            e.bind('<Return>',lambda _:self.submit())
        self.msg=tk.StringVar(value='Student accounts only. Admin access is configured locally by the project operator.')
        tk.Label(shell,textvariable=self.msg,bg=T.PANEL,fg=T.MUTED,font=('Segoe UI',9),wraplength=385,justify='left').pack(anchor='w',padx=38,pady=15)
        button(shell,'SIGN IN' if self.mode=='login' else 'CREATE ACCOUNT',self.submit).pack(fill='x',padx=38,pady=(2,10))
        tk.Button(shell,text='Create a student account' if self.mode=='login' else 'Back to sign in',command=self.toggle,bg=T.PANEL,fg=T.CYAN,relief='flat',font=('Segoe UI',10,'bold')).pack(pady=4)
        if self.mode=='login':
            tk.Button(shell,text='First-time administrator setup',command=self.setup_admin,bg=T.PANEL,fg=T.MUTED,relief='flat',font=('Segoe UI',9)).pack(pady=12)
            tk.Button(self,text='← Back to project welcome',command=self.on_back,bg=T.BG,fg=T.MUTED,relief='flat').place(relx=.05,rely=.05)
    def toggle(self):self.mode='register' if self.mode=='login' else 'login';self._draw()
    def submit(self):
        username=self.fields['username'].get().strip();password=self.fields['password'].get()
        try:
            if self.mode=='register':
                if password!=self.fields['confirm'].get():raise ValueError('Passwords do not match.')
                uid=database.register(username,password);user=database.authenticate(username,password)
            else:
                user=database.authenticate(username,password)
                if not user:raise ValueError('Username or password is incorrect.')
            self.on_login(user)
        except (ValueError,PermissionError) as e:messagebox.showerror('Could not continue',str(e),parent=self)
    def setup_admin(self):
        if messagebox.askyesno('Administrator setup','This one-time setup creates the first administrator on this computer. Continue only on a trusted machine.',parent=self):
            setup_key=simpledialog.askstring('Administrator setup','Enter the one-time code configured in CAMPUS_ADMIN_SETUP_TOKEN:',show='●',parent=self)
            if not setup_key:return
            username=simpledialog.askstring('Administrator setup','New administrator username:',parent=self)
            if not username:return
            password=simpledialog.askstring('Administrator setup','Create a strong password (10+ characters):',show='●',parent=self)
            if not password:return
            try:
                database.bootstrap_admin(username,password,setup_key)
                messagebox.showinfo('Administrator created','The first administrator is ready. This local one-time setup is now closed. Sign in with the credentials you just created.',parent=self)
            except (ValueError,PermissionError) as e:messagebox.showerror('Setup unavailable',str(e),parent=self)
