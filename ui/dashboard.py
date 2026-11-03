import tkinter as tk
from tkinter import ttk,messagebox,simpledialog,filedialog
from datetime import date
import database
from config import CATEGORIES
from matching import find_matches
from ui import theme as T
from ui.common import button,card,entry,label

class Dashboard(tk.Frame):
    def __init__(self,master,user,on_logout):
        super().__init__(master,bg=T.BG);self.user=user;self.on_logout=on_logout;self.page='Overview';self.filters={};self._chrome();self.show('Overview')
    def _chrome(self):
        style=ttk.Style();style.theme_use('clam')
        style.configure('Treeview',background=T.PANEL,fieldbackground=T.PANEL,foreground=T.TEXT,rowheight=34,borderwidth=0,font=('Segoe UI',9))
        style.configure('Treeview.Heading',background=T.PANEL2,foreground=T.CYAN,font=('Segoe UI',9,'bold'))
        style.map('Treeview',background=[('selected','#153755')],foreground=[('selected',T.TEXT)])
        style.configure('TCombobox',fieldbackground='#091625',background=T.PANEL2,foreground=T.TEXT,arrowcolor=T.CYAN)
        style.map('TCombobox',fieldbackground=[('readonly','#091625')],foreground=[('readonly',T.TEXT)],background=[('readonly',T.PANEL2)])
        bar=tk.Frame(self,bg='#091523',highlightbackground=T.LINE,highlightthickness=1);bar.pack(fill='x')
        label(bar,text='◈  CAMPUSFIND',bg='#091523',fg=T.CYAN,font=('Segoe UI',13,'bold')).pack(side='left',padx=24,pady=15)
        label(bar,text='RECOVERY NETWORK   /   SRM KTR',bg='#091523',fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(side='left',padx=12)
        label(bar,text=f"{self.user['username']}  ·  {self.user['role'].upper()}",bg='#091523',fg=T.TEXT).pack(side='right',padx=(8,22))
        button(bar,'Sign out',self.on_logout,'secondary').pack(side='right',pady=7)
        body=tk.Frame(self,bg=T.BG);body.pack(fill='both',expand=True)
        side=tk.Frame(body,bg='#091523',width=220);side.pack(side='left',fill='y');side.pack_propagate(False)
        nav=['Overview','Browse & search','Report lost','Report found','My reports','My claims','Notifications']
        if self.user['role']=='admin':nav += ['Claim review','Report moderation','User management','Analytics']
        for name in nav:
            b=tk.Button(side,text='  '+name,anchor='w',command=lambda n=name:self.show(n),bg='#091523',fg=T.MUTED,activebackground=T.PANEL2,activeforeground=T.CYAN,relief='flat',font=('Segoe UI',10,'bold'),padx=18,pady=13,cursor='hand2');b.pack(fill='x',padx=8,pady=2)
        self.content=tk.Frame(body,bg=T.BG);self.content.pack(side='left',fill='both',expand=True,padx=28,pady=23)
    def _clear(self):
        for w in self.content.winfo_children():w.destroy()
    def _heading(self,title,subtitle):
        label(self.content,text=title,bg=T.BG,font=('Segoe UI',23,'bold')).pack(anchor='w')
        label(self.content,text=subtitle,bg=T.BG,fg=T.MUTED).pack(anchor='w',pady=(4,20))
    def show(self,page):
        self.page=page;self._clear()
        if page=='Overview':self.overview()
        elif page in ('Report lost','Report found'):self.report(page.split()[-1].lower())
        elif page in ('Browse & search','My reports'):self.browse(own=page=='My reports')
        elif page=='My claims':self.claims()
        elif page=='Claim review':self.review()
        elif page=='Notifications':self.notice_list()
        elif page=='Report moderation':self.moderation()
        elif page=='User management':self.users()
        elif page=='Analytics':self.analytics()
    def overview(self):
        c=database.counts();self._heading('Good day, '+self.user['username'], 'Your campus recovery desk is ready. Here is the live activity across reports and claims.')
        stats=[('LOST REPORTS',c['lost'],T.CYAN),('FOUND ITEMS',c['found'],T.VIOLET),('PENDING CLAIMS',c['pending_claims'],T.AMBER),('RETURNED',c['returned'],T.GREEN)]
        row=tk.Frame(self.content,bg=T.BG);row.pack(fill='x')
        for title,value,color in stats:
            box=card(row);box.pack(side='left',fill='x',expand=True,padx=(0,12));label(box,text=title,fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',padx=17,pady=(15,4));label(box,text=str(value),fg=color,font=('Segoe UI',25,'bold')).pack(anchor='w',padx=17,pady=(0,15))
        label(self.content,text='RECENT CAMPUS REPORTS',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',pady=(22,8))
        self._table(self.content,database.search_items(),compact=True)
        if self.user['role']=='admin':label(self.content,text=f"Administration  ·  {c['students']} students  ·  {c['approved_claims']} approved  ·  {c['rejected_claims']} rejected",bg=T.BG,fg=T.MUTED).pack(anchor='w',pady=14)
        label(self.content,text='Potential matches are explainable suggestions. Administrators review all ownership claims manually.',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9)).pack(anchor='w',pady=9)
        recent=database.notifications(self.user['id'])[:3]
        if recent:
            label(self.content,text='RECENT NOTIFICATIONS',bg=T.BG,fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',pady=(8,4))
            for n in recent:label(self.content,text=f"{n['title']}  ·  {n['body']}",bg=T.PANEL,fg=T.TEXT,anchor='w',padx=12,pady=8).pack(fill='x',pady=2)
    def report(self,kind):
        self._heading('Report a '+kind+' item','Share enough detail to help a campus community member recognize it. Contact details stay private.')
        form=card(self.content);form.pack(fill='x',anchor='nw');form.grid_columnconfigure(1,weight=1);form.grid_columnconfigure(3,weight=1)
        self.form={}
        def field(key,title,r,col=0,wide=False):
            label(form,text=title,fg=T.MUTED,font=('Segoe UI',9,'bold')).grid(row=r*2,column=col,sticky='w',padx=16,pady=(12,4),columnspan=2)
            if key=='category':
                w=ttk.Combobox(form,values=CATEGORIES,state='readonly');w.set(CATEGORIES[0])
            elif key=='description':w=tk.Text(form,height=4,bg='#091625',fg=T.TEXT,insertbackground=T.CYAN,relief='flat',font=('Segoe UI',10),wrap='word')
            else:w=entry(form);w.insert(0,date.today().isoformat() if key=='event_date' else '')
            w.grid(row=r*2+1,column=col,sticky='ew',padx=16,pady=(0,4),columnspan=2,ipady=7 if key!='description' else 0);self.form[key]=w
        field('item_name','ITEM NAME',0,0);field('category','CATEGORY',0,2);field('location','LOCATION',1,0);field('event_date','DATE  ·  YYYY-MM-DD',1,2);field('event_time','APPROXIMATE TIME',2,0);field('contact','PRIVATE CONTACT DETAILS',2,2);field('description','DESCRIPTION',3,0,True)
        self.form['type']=kind
        self.image_path=None
        tk.Button(form,text='＋ Attach a photograph (optional)',command=self.pick_image,bg=T.PANEL2,fg=T.CYAN,relief='flat').grid(row=9,column=0,sticky='w',padx=16,pady=8)
        self.image_label=tk.StringVar(value='No image selected');label(form,textvariable=self.image_label,fg=T.MUTED).grid(row=9,column=1,columnspan=2,sticky='w')
        button(form,'SUBMIT REPORT',self.submit_report).grid(row=10,column=0,sticky='w',padx=16,pady=16)
    def pick_image(self):
        p=filedialog.askopenfilename(filetypes=[('Images','*.png *.jpg *.jpeg *.webp')],parent=self)
        if p:self.image_path=p;self.image_label.set(p.split('/')[-1].split('\\')[-1])
    def submit_report(self):
        f=self.form;data={k:(w.get('1.0','end').strip() if isinstance(w,tk.Text) else w.get().strip()) for k,w in f.items() if k!='type'};data['type']=f['type'];data['image_path']=self.image_path
        try:database.create_item(self.user['id'],data);messagebox.showinfo('Report submitted','Your report is now visible in the campus browse list.',parent=self);self.show('My reports')
        except ValueError as e:messagebox.showerror('Please review the form',str(e),parent=self)
    def browse(self,own=False,rows=None):
        self._heading('My reports' if own else 'Browse & search','Search descriptions and locations. Private contact details and ownership evidence are never shown in public listings.')
        if not own:
            tools=tk.Frame(self.content,bg=T.BG);tools.pack(fill='x',pady=(0,12))
            self.q=entry(tools,width=25);self.q.pack(side='left',ipady=9);self.q.insert(0,'Search name or description')
            self.ftype=ttk.Combobox(tools,values=['Any type','lost','found'],state='readonly',width=13);self.ftype.set('Any type');self.ftype.pack(side='left',padx=8)
            self.fcat=ttk.Combobox(tools,values=['Any category',*CATEGORIES],state='readonly',width=18);self.fcat.set('Any category');self.fcat.pack(side='left',padx=8)
            button(tools,'SEARCH',lambda:self.browse_results(False),'secondary').pack(side='left')
        self._table(self.content, database.my_items(self.user['id']) if own else (rows if rows is not None else database.search_items()), own=own)
    def browse_results(self,own=False):
        if self.page!='Browse & search':return
        f={'keyword':self.q.get().strip() if self.q.get()!='Search name or description' else '', 'type':self.ftype.get() if self.ftype.get()!='Any type' else None,'category':self.fcat.get() if self.fcat.get()!='Any category' else None}
        rows=database.search_items(f)
        if hasattr(self,'resulttree'):
            for iid in self.resulttree.get_children():self.resulttree.delete(iid)
            for r in rows:self.resulttree.insert('','end',iid=str(r['id']),values=(r['type'].upper(),r['item_name'],r['category'],r['location'],r['event_date'],r['status'].replace('_',' ')))
    def _table(self,parent,rows,own=False,compact=False):
        wrap=card(parent);wrap.pack(fill='both',expand=True)
        cols=('type','item_name','category','location','event_date','status')
        tree=ttk.Treeview(wrap,columns=cols,show='headings',height=8 if compact else 15)
        for col,title,width in zip(cols,('TYPE','ITEM','CATEGORY','LOCATION','DATE','STATUS'),(85,210,130,190,110,120)):
            tree.heading(col,text=title);tree.column(col,width=width,anchor='w')
        for r in rows:tree.insert('','end',iid=str(r['id']),values=(r['type'].upper(),r['item_name'],r['category'],r['location'],r['event_date'],r['status'].replace('_',' ')))
        self.reporttree=tree;self.reportrows=rows;self.resulttree=tree
        tree.pack(fill='both',expand=True,padx=10,pady=10)
        if not compact:
            actions=tk.Frame(parent,bg=T.BG);actions.pack(fill='x',pady=10)
            def selected():
                sel=tree.selection()
                if not sel:messagebox.showinfo('Select a report','Choose a report in the list first.',parent=self);return None
                return next((r for r in rows if str(r['id'])==sel[0]),None)
            if own or self.user['role']=='student':
                button(actions,'FIND POSSIBLE MATCHES',lambda:self.show_matches(selected()),'secondary').pack(side='left')
            if not own and self.user['role']=='student':
                button(actions,'SUBMIT OWNERSHIP CLAIM',lambda:self.claim_selected(selected(),rows),'primary').pack(side='left',padx=8)
                label(actions,text='Select a found item to claim; evidence is private.',bg=T.BG,fg=T.MUTED).pack(side='left',padx=10)
    def show_matches(self,item):
        if not item:return
        rows=database.search_items({'type':'found' if item['type']=='lost' else 'lost'})
        matches=find_matches(item,[r for r in rows if r['id']!=item['id']])
        text='\n'.join(f"{m['score']}%  ·  {m['item_name']}  ·  {m['location']}\n      {'; '.join(m['reasons'])}" for m in matches) or 'No opposite-type reports to compare yet.'
        messagebox.showinfo('Explainable potential matches',text+'\n\nRule-based similarity only; verify details yourself.',parent=self)
    def claim_selected(self,item,rows):
        if not item:return
        if item['type']!='found':messagebox.showinfo('Choose a found item','Claims are submitted for found items.',parent=self);return
        evidence=simpledialog.askstring('Ownership claim','Provide private identifying details that help verify ownership. This is only visible to authorized administrators.',parent=self)
        if evidence:
            try:database.create_claim(item['id'],self.user['id'],evidence);messagebox.showinfo('Claim submitted','Your claim is pending administrator review.',parent=self);self.show('My claims')
            except ValueError as e:messagebox.showerror('Could not submit claim',str(e),parent=self)
    def claims(self):
        self._heading('My claims','Track ownership claims you have submitted and their review status.')
        rows=database.list_claims(self.user);self._claim_table(rows)
    def _claim_table(self,rows,admin=False):
        cols=('item_name','claimant','status','created_at','admin_remark') if admin else ('item_name','status','created_at','admin_remark')
        frame=card(self.content);frame.pack(fill='both',expand=True);tree=ttk.Treeview(frame,columns=cols,show='headings',height=16)
        titles={'item_name':'ITEM','claimant':'CLAIMANT','status':'STATUS','created_at':'SUBMITTED','admin_remark':'ADMIN REMARK'}
        for c in cols:tree.heading(c,text=titles[c]);tree.column(c,width=170 if c in ('item_name','admin_remark') else 125)
        for r in rows:tree.insert('','end',iid=str(r['id']),values=tuple(r.get(c,'') for c in cols))
        tree.pack(fill='both',expand=True,padx=10,pady=10);self.claimtree=tree;self.claimrows=rows
    def review(self):
        self._heading('Claim review','Inspect private evidence and record a decision. Approval is an administrator-only action.')
        rows=database.list_claims(self.user);self._claim_table(rows,True)
        actions=tk.Frame(self.content,bg=T.BG);actions.pack(fill='x',pady=10)
        button(actions,'VIEW PRIVATE EVIDENCE',self.view_evidence,'secondary').pack(side='left')
        button(actions,'APPROVE CLAIM',lambda:self.decide('APPROVED'),'success').pack(side='left',padx=8)
        button(actions,'REJECT CLAIM',lambda:self.decide('REJECTED'),'danger').pack(side='left')
        button(actions,'MARK ITEM RETURNED',self.return_item,'secondary').pack(side='left',padx=8)
    def current_claim(self):
        s=self.claimtree.selection()
        if not s:messagebox.showinfo('Select a claim','Choose a claim first.',parent=self);return None
        return next((r for r in self.claimrows if str(r['id'])==s[0]),None)
    def view_evidence(self):
        r=self.current_claim()
        if r:messagebox.showinfo('Private claim evidence',r['evidence'],parent=self)
    def decide(self,status):
        r=self.current_claim()
        if not r:return
        if r['status']!='PENDING':messagebox.showinfo('Already reviewed','Only pending claims can be reviewed.',parent=self);return
        remark=simpledialog.askstring('Administrative remark','Optional note for the student:',parent=self) or ''
        try:database.review_claim(self.user,r['id'],status,remark);self.show('Claim review')
        except (ValueError,PermissionError) as e:messagebox.showerror('Could not review claim',str(e),parent=self)
    def return_item(self):
        r=self.current_claim()
        if not r:return
        try:database.mark_returned(self.user,r['item_id']);messagebox.showinfo('Item updated','Item marked returned; a notification was created.',parent=self);self.show('Claim review')
        except (ValueError,PermissionError) as e:messagebox.showerror('Could not update item',str(e),parent=self)
    def analytics(self):
        c=database.counts();self._heading('Campus analytics','Live counts derived from this local SQLite database.')
        grid=tk.Frame(self.content,bg=T.BG);grid.pack(anchor='nw')
        for i,(name,num) in enumerate(c.items()):
            box=card(grid,width=220,height=105);box.grid(row=i//3,column=i%3,padx=8,pady=8,sticky='nsew');box.pack_propagate(False)
            label(box,text=name.replace('_',' ').upper(),fg=T.MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',padx=16,pady=(15,4));label(box,text=str(num),fg=T.CYAN,font=('Segoe UI',24,'bold')).pack(anchor='w',padx=16)
    def notice_list(self):
        self._heading('Notifications','Persistent updates for reports, potential matches, and claim decisions.')
        rows=database.notifications(self.user['id'])
        if not rows:label(self.content,text='You are all caught up.',bg=T.BG,fg=T.MUTED).pack(anchor='w')
        for n in rows:
            c=card(self.content);c.pack(fill='x',pady=5);label(c,text=n['title'],font=('Segoe UI',11,'bold')).pack(anchor='w',padx=16,pady=(12,3));label(c,text=n['body'],fg=T.MUTED).pack(anchor='w',padx=16,pady=(0,12))
    def moderation(self):
        self._heading('Report moderation','Review campus reports. Administrators can mark an item as returned after handover.')
        rows=database.search_items();self._table(self.content,rows)
        button(self.content,'MARK SELECTED REPORT RETURNED',self.moderate_return,'secondary').pack(anchor='w',pady=8)
    def moderate_return(self):
        if not hasattr(self,'reporttree'):messagebox.showinfo('Select a report','Select a report first.',parent=self);return
        sel=self.reporttree.selection()
        if not sel:return
        try:database.mark_returned(self.user,int(sel[0]));self.show('Report moderation')
        except (ValueError,PermissionError) as e:messagebox.showerror('Could not update report',str(e),parent=self)
    def users(self):
        self._heading('User management','Registered account list. Student access is assigned at registration; administrator roles are not self-service.')
        with database.connect() as c:rows=[dict(r) for r in c.execute('SELECT id,username,role,created_at FROM users ORDER BY id DESC')]
        frame=card(self.content);frame.pack(fill='both',expand=True);tree=ttk.Treeview(frame,columns=('username','role','created_at'),show='headings',height=16)
        for col,title in [('username','USERNAME'),('role','ROLE'),('created_at','CREATED')]:tree.heading(col,text=title);tree.column(col,width=210)
        for r in rows:tree.insert('','end',values=(r['username'],r['role'].upper(),r['created_at']))
        tree.pack(fill='both',expand=True,padx=10,pady=10)
