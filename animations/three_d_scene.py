"""Maliang 3D showcase probe and a resilient Canvas fallback."""
import math, tkinter as tk

def add_maliang_scene(parent):
    """Create a real Maliang 3D Space + cuboid if the installed extension works."""
    try:
        from maliang import three
        # Maliang's canvas container bookkeeping expects a Maliang parent. A
        # standard Tk Frame works as a host once it exposes that small registry.
        if not hasattr(parent, 'canvases'): parent.canvases=[]
        if not hasattr(parent, 'ratios'): parent.ratios=[1.0,1.0]
        space=three.Space(parent,bg='#07111f',highlightthickness=0,auto_zoom=True,keep_ratio='min')
        space.light.update(bg='#07111f');space.dark.update(bg='#07111f')
        space.configure(bg='#07111f')
        space.place(relwidth=1,relheight=1)
        space.update()
        box=three.Cuboid(space,-80,-80,-80,160,160,160,boardwidth=3,color_outline_up='#5bd5ff',color_outline_down='#495fd9',color_outline_left='#4ebfff',color_outline_right='#9a75ff',color_outline_front='#52d5ed',color_outline_back='#5969dc')
        box.rotate(.35,.48,.22,center=(0,0,0));box.update();space.space_sort()
        space._campus_box=box
        def animate():
            if not space.winfo_exists():return
            try:box.rotate(.004,.009,.003,center=(0,0,0));box.update();space.space_sort();space.after(33,animate)
            except tk.TclError:pass
        space.after(33,animate)
        return space
    except Exception:
        return None

class CubeFallback:
    def __init__(self,canvas):
        self.c=canvas;self.angle=0;self.after=None;canvas.bind('<Configure>',lambda e:self.draw())
    def start(self): self.draw()
    def stop(self):
        if self.after:
            try:self.c.after_cancel(self.after)
            except tk.TclError:pass
    def draw(self):
        c=self.c;c.delete('cube');w=max(1,c.winfo_width());h=max(1,c.winfo_height());a=self.angle
        pts=[]
        for x in (-1,1):
            for y in (-1,1):
                for z in (-1,1):
                    xx=x*math.cos(a)+z*math.sin(a);zz=-x*math.sin(a)+z*math.cos(a); yy=y*math.cos(a*.72)-zz*math.sin(a*.72);zz=y*math.sin(a*.72)+zz*math.cos(a*.72)
                    scale=105/(2.7+zz);pts.append((w*.5+xx*scale,h*.5+yy*scale,zz))
        edges=[(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]
        for i,j in edges:c.create_line(*pts[i][:2],*pts[j][:2],fill='#3bc8ef' if (i+j)%2==0 else '#8572ff',width=2,tags='cube')
        self.angle+=.016
        self.after=c.after(33,self.draw)
