import tkinter as tk
from animations.particles import ParticleField
from animations.three_d_scene import add_maliang_scene,CubeFallback
from config import TEAM
from ui import theme as T
from ui.common import button

class Welcome(tk.Frame):
    def __init__(self,master,on_enter):
        super().__init__(master,bg=T.BG);self.on_enter=on_enter
        self.canvas=tk.Canvas(self,bg=T.BG,highlightthickness=0);self.canvas.place(relwidth=1,relheight=1)
        self.particles=ParticleField(self.canvas);self.particles.start()
        self.after(100,self._build)
    def _build(self):
        if not self.winfo_exists():return
        # Structured foreground sits above the animated ambient canvas.
        top=tk.Frame(self,bg=T.BG);top.place(relx=.07,rely=.045)
        tk.Label(top,text='SRM  /  KTR',bg=T.BG,fg=T.CYAN,font=('Segoe UI',10,'bold')).pack(side='left')
        tk.Label(top,text='     CAMPUS RECOVERY NETWORK',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(side='left')
        main=tk.Frame(self,bg=T.BG);main.place(relx=.075,rely=.15,relwidth=.85,relheight=.76)
        left=tk.Frame(main,bg=T.BG);left.place(relx=0,rely=.02,relwidth=.61,relheight=.96)
        tk.Label(left,text='APP TKINTER PROJECT',bg=T.BG,fg=T.CYAN,font=('Segoe UI',11,'bold')).pack(anchor='w',pady=(0,15))
        tk.Label(left,text='CAMPUS LOST & FOUND\nMANAGEMENT SYSTEM',bg=T.BG,fg=T.TEXT,font=('Segoe UI',26,'bold'),justify='left').pack(anchor='w')
        tk.Label(left,text='A thoughtful way to reunite campus belongings with their owners.',bg=T.BG,fg=T.MUTED,font=('Segoe UI',12)).pack(anchor='w',pady=(12,17))
        tk.Label(left,text='SRM Institute of Science and Technology',bg=T.BG,fg=T.TEXT,font=('Segoe UI',12,'bold')).pack(anchor='w')
        tk.Label(left,text='Kattankulathur Campus',bg=T.BG,fg=T.MUTED,font=('Segoe UI',10)).pack(anchor='w',pady=(4,2))
        tk.Label(left,text='Second Year | Semester III',bg=T.BG,fg=T.MUTED,font=('Segoe UI',10)).pack(anchor='w',pady=(0,12))
        team=tk.Frame(left,bg=T.BG);team.pack(anchor='w',fill='x')
        for name,role in TEAM:
            row=tk.Frame(team,bg=T.PANEL,highlightbackground=T.LINE,highlightthickness=1);row.pack(fill='x',pady=3)
            tk.Label(row,text=name,bg=T.PANEL,fg=T.TEXT,font=('Segoe UI',10,'bold'),anchor='w').pack(side='left',padx=12,pady=7)
            tk.Label(row,text=role,bg='#12324a' if role=='TEAM LEADER' else '#1a2638',fg=T.CYAN if role=='TEAM LEADER' else T.MUTED,font=('Segoe UI',8,'bold'),padx=10,pady=4,width=14).pack(side='right',padx=9)
        actions=tk.Frame(left,bg=T.BG);actions.pack(anchor='w',pady=(16,8))
        button(actions,'ENTER APPLICATION  →',self.on_enter).pack(side='left')
        tk.Label(actions,text='   Secure · Student-led · Campus focused',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9)).pack(side='left',padx=9)
        tk.Label(left,text='Independent student academic prototype. Not an official SRMIST service.',bg=T.BG,fg='#798da5',font=('Segoe UI',8)).pack(anchor='w',pady=(4,0))
        right=tk.Frame(main,bg=T.BG);right.place(relx=.65,rely=.13,relwidth=.35,relheight=.75)
        scene=add_maliang_scene(right)
        if scene is None:
            fallback=tk.Canvas(right,bg=T.BG,highlightthickness=0);fallback.place(relwidth=1,relheight=1);self.fallback=CubeFallback(fallback);self.fallback.start()
        tk.Label(right,text='RETURN TO WHAT MATTERS',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9,'bold')).place(relx=.5,rely=.84,anchor='center')
    def destroy(self):
        if hasattr(self,'particles'):self.particles.stop()
        if hasattr(self,'fallback'):self.fallback.stop()
        super().destroy()
