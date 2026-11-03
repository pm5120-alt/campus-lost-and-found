import math, random, time
import tkinter as tk

class ParticleField:
    def __init__(self, canvas:tk.Canvas, enabled=True):
        self.canvas=canvas; self.enabled=enabled; self.items=[]; self.running=False; self.after_id=None; self.started=time.monotonic()
        self.canvas.bind('<Configure>',self._resize,add='+')
    def start(self):
        if self.running or not self.enabled:return
        self.running=True; self._resize(None); self._tick()
    def stop(self):
        self.running=False
        if self.after_id:
            try:self.canvas.after_cancel(self.after_id)
            except tk.TclError:pass
            self.after_id=None
    def _resize(self,_):
        if not self.enabled:return
        w=max(1,self.canvas.winfo_width());h=max(1,self.canvas.winfo_height())
        if not self.items:
            self.items=[{'x':random.random()*w,'y':random.random()*h,'r':random.choice([1,1,2]),'vx':random.uniform(-.18,.18),'vy':random.uniform(-.14,.14),'phase':random.random()*6.28} for _ in range(38)]
        for p in self.items:p['x']%=w;p['y']%=h
    def _tick(self):
        if not self.running:return
        c=self.canvas
        try:
            c.delete('ambient'); w=c.winfo_width(); h=c.winfo_height(); t=time.monotonic()-self.started
            pts=[]
            for p in self.items:
                p['x']=(p['x']+p['vx'])%w;p['y']=(p['y']+p['vy'])%h
                pts.append((p['x'],p['y'],p['phase']))
            for i,(x,y,_) in enumerate(pts):
                for xx,yy,_ in pts[i+1:]:
                    d=math.hypot(x-xx,y-yy)
                    if d<118:c.create_line(x,y,xx,yy,fill='#142b4b',width=.7,tags='ambient')
            for x,y,phase in pts:
                r=1.1+0.8*(.5+.5*math.sin(t+phase));c.create_oval(x-r,y-r,x+r,y+r,fill='#31b9e9',outline='',tags='ambient')
            for i in range(3):
                x=w*(.25+.36*i)+math.sin(t*.18+i)*75;y=h*(.28+.21*(i%2))+math.cos(t*.16+i)*45
                c.create_oval(x-130,y-130,x+130,y+130,fill='',outline='#101d35',width=1,tags='ambient')
            self.after_id=c.after(40,self._tick)
        except tk.TclError:self.stop()
