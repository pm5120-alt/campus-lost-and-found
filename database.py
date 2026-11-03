from __future__ import annotations
import hashlib, hmac, os, secrets, shutil, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from config import BASE_DIR, DATA_DIR, DB_PATH, UPLOAD_DIR, PBKDF2_ITERATIONS, MAX_IMAGE_BYTES
from validators import validate_image, validate_item

class DatabaseError(RuntimeError): pass

@contextmanager
def connect(path: str | Path = DB_PATH):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON"); conn.execute("PRAGMA busy_timeout=10000")
    try: yield conn
    finally: conn.close()

def setup_database(path: str | Path = DB_PATH):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.stat().st_size and not p.with_suffix(p.suffix+".bak").exists(): shutil.copy2(p,p.with_suffix(p.suffix+".bak"))
    with connect(p) as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT NOT NULL COLLATE NOCASE UNIQUE, password_hash TEXT NOT NULL, salt TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student','admin')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), type TEXT NOT NULL CHECK(type IN ('lost','found')), item_name TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL, location TEXT NOT NULL, event_date TEXT NOT NULL, event_time TEXT NOT NULL DEFAULT '', image_path TEXT, contact TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','IN_REVIEW','RETURNED')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS claims(id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL REFERENCES items(id), claimant_id INTEGER NOT NULL REFERENCES users(id), evidence TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','APPROVED','REJECTED')), admin_remark TEXT NOT NULL DEFAULT '', reviewed_by INTEGER REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, reviewed_at TEXT, UNIQUE(item_id, claimant_id));
        CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, body TEXT NOT NULL, read INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_items_type_status_date ON items(type,status,event_date); CREATE INDEX IF NOT EXISTS idx_items_owner ON items(owner_id); CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status); CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id,read);
        ''')
        # Safe additive migration of older CampusFinds databases.
        cols={r[1] for r in c.execute("PRAGMA table_info(users)")}
        if "role" not in cols: c.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")

def _password(password: str, salt: bytes) -> bytes: return hashlib.pbkdf2_hmac("sha256",password.encode(),salt,PBKDF2_ITERATIONS)
def register(username: str,password: str,role: str="student",path: str|Path=DB_PATH) -> int:
    if role != "student": raise PermissionError("Administrator accounts cannot be self-registered.")
    if not username.strip() or len(username)>80: raise ValueError("Enter a username up to 80 characters.")
    from validators import validate_password
    problem=validate_password(password)
    if problem: raise ValueError(problem)
    salt=secrets.token_bytes(16)
    try:
        with connect(path) as c:
            cur=c.execute("INSERT INTO users(username,password_hash,salt,role) VALUES(?,?,?,'student')",(username.strip(),_password(password,salt).hex(),salt.hex()))
            return cur.lastrowid
    except sqlite3.IntegrityError as e: raise ValueError("That username is already registered.") from e
def authenticate(username: str,password: str,path: str|Path=DB_PATH):
    with connect(path) as c: row=c.execute("SELECT * FROM users WHERE username=?",(username.strip(),)).fetchone()
    if not row or not hmac.compare_digest(_password(password,bytes.fromhex(row['salt'])).hex(),row['password_hash']): return None
    return dict(row)
def bootstrap_admin(username: str,password: str,setup_key: str,path: str|Path=DB_PATH) -> int:
    expected=os.environ.get('CAMPUS_ADMIN_SETUP_TOKEN','')
    if len(expected)<24: raise PermissionError("Set CAMPUS_ADMIN_SETUP_TOKEN to a random secret of at least 24 characters before launching the app.")
    if not hmac.compare_digest(setup_key,expected): raise PermissionError("The administrator setup code is incorrect.")
    if not username.strip() or len(username)>80: raise ValueError("Enter an administrator username up to 80 characters.")
    marker=Path(path).with_suffix('.admin_setup')
    if marker.exists(): raise PermissionError("Administrator setup has already been completed.")
    from validators import validate_password
    err=validate_password(password)
    if err: raise ValueError(err)
    salt=secrets.token_bytes(16)
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        if c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone(): c.rollback(); raise PermissionError("An administrator already exists.")
        cur=c.execute("INSERT INTO users(username,password_hash,salt,role) VALUES(?,?,?,'admin')",(username.strip(),_password(password,salt).hex(),salt.hex()))
        c.commit()
    marker.write_text(hashlib.sha256(setup_key.encode()).hexdigest(),encoding='ascii')
    return cur.lastrowid
def create_item(owner_id: int,data: dict,path: str|Path=DB_PATH) -> int:
    err=validate_item(data)
    if err: raise ValueError(err)
    image=data.get('image_path')
    if image:
        err=validate_image(image)
        if err: raise ValueError(err)
        UPLOAD_DIR.mkdir(exist_ok=True); src=Path(image); name=f"{secrets.token_hex(16)}{src.suffix.lower()}"; dst=UPLOAD_DIR/name; shutil.copyfile(src,dst); image=str(Path('uploads')/name)
    with connect(path) as c:
        cur=c.execute("INSERT INTO items(owner_id,type,item_name,category,description,location,event_date,event_time,image_path,contact) VALUES(?,?,?,?,?,?,?,?,?,?)",(owner_id,data['type'],data['item_name'].strip(),data['category'],data['description'].strip(),data['location'].strip(),data['event_date'],data.get('event_time',''),image,data.get('contact','').strip()))
        item={**data,'id':cur.lastrowid}
        from matching import explain_match
        candidates=c.execute("SELECT id,owner_id,type,item_name,category,description,location,event_date FROM items WHERE type<>? AND status<>'RETURNED' AND id<>? AND owner_id<>? ORDER BY id DESC LIMIT 100",(data['type'],cur.lastrowid,owner_id)).fetchall()
        for candidate in candidates:
            match=explain_match(item,dict(candidate))
            if match['score']>=65:
                summary=f"{data['item_name']} may match {candidate['item_name']} ({match['score']}%). Review the report details."
                c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(owner_id,'Potential item match',summary))
                c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(candidate['owner_id'],'Potential item match',summary))
        return cur.lastrowid
def search_items(filters: dict|None=None,viewer_id: int|None=None,is_admin=False,path: str|Path=DB_PATH):
    f=filters or {}; clauses=["i.status <> 'RETURNED' OR i.status='RETURNED'"]; args=[]
    for key,col in [('type','i.type'),('category','i.category'),('status','i.status')]:
        if f.get(key): clauses.append(f"{col}=?");args.append(f[key])
    for key in ('keyword','location','date'):
        if f.get(key):
            col={'keyword':"(i.item_name LIKE ? OR i.description LIKE ? OR i.category LIKE ?)",'location':'i.location LIKE ?','date':'i.event_date=?'}[key]
            clauses.append(col); args.extend(([f"%{f[key]}%"]*3) if key=='keyword' else ([f"%{f[key]}%"] if key=='location' else [f[key]]))
    sql="SELECT i.id,i.owner_id,i.type,i.item_name,i.category,i.description,i.location,i.event_date,i.event_time,i.status,i.image_path,i.created_at, u.username FROM items i JOIN users u ON u.id=i.owner_id WHERE "+" AND ".join(f"({x})" for x in clauses)+" ORDER BY i.id DESC"
    with connect(path) as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
def my_items(user_id,path: str|Path=DB_PATH):
    with connect(path) as c:return [dict(r) for r in c.execute("SELECT * FROM items WHERE owner_id=? ORDER BY id DESC",(user_id,))]
def counts(path: str|Path=DB_PATH):
    with connect(path) as c:
        return {"students":c.execute("SELECT count(*) FROM users WHERE role='student'").fetchone()[0],"lost":c.execute("SELECT count(*) FROM items WHERE type='lost'").fetchone()[0],"found":c.execute("SELECT count(*) FROM items WHERE type='found'").fetchone()[0],"pending_claims":c.execute("SELECT count(*) FROM claims WHERE status='PENDING'").fetchone()[0],"approved_claims":c.execute("SELECT count(*) FROM claims WHERE status='APPROVED'").fetchone()[0],"rejected_claims":c.execute("SELECT count(*) FROM claims WHERE status='REJECTED'").fetchone()[0],"returned":c.execute("SELECT count(*) FROM items WHERE status='RETURNED'").fetchone()[0]}
def create_claim(item_id:int,claimant_id:int,evidence:str,path: str|Path=DB_PATH):
    if not evidence.strip() or len(evidence)>2000: raise ValueError("Add private identifying evidence (up to 2,000 characters).")
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE"); item=c.execute("SELECT * FROM items WHERE id=?",(item_id,)).fetchone()
        claimant=c.execute("SELECT role FROM users WHERE id=?",(claimant_id,)).fetchone()
        if not claimant or claimant['role']!='student':c.rollback();raise PermissionError("Only student accounts can submit ownership claims.")
        if not item or item['type']!='found' or item['status']=='RETURNED' or item['owner_id']==claimant_id: c.rollback(); raise ValueError("This item is not available to claim.")
        try: cur=c.execute("INSERT INTO claims(item_id,claimant_id,evidence) VALUES(?,?,?)",(item_id,claimant_id,evidence.strip()))
        except sqlite3.IntegrityError as e: c.rollback(); raise ValueError("You have already submitted a claim for this item.") from e
        c.execute("UPDATE items SET status='IN_REVIEW' WHERE id=?",(item_id,)); c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(item['owner_id'],'New claim received',f"A student submitted a claim for {item['item_name']}."))
        c.execute("INSERT INTO notifications(user_id,title,body) SELECT id,'New claim submitted',? FROM users WHERE role='admin'",(f"A student submitted a claim for {item['item_name']}.",))
        c.commit(); return cur.lastrowid
def list_claims(user:dict,path: str|Path=DB_PATH):
    sql="SELECT c.id,c.item_id,c.claimant_id,c.evidence,c.status,c.admin_remark,c.created_at,i.item_name,i.owner_id,u.username claimant FROM claims c JOIN items i ON i.id=c.item_id JOIN users u ON u.id=c.claimant_id"
    args=()
    if user['role']!='admin': sql+=" WHERE c.claimant_id=?";args=(user['id'],)
    with connect(path) as c:return [dict(r) for r in c.execute(sql+" ORDER BY c.id DESC",args)]
def review_claim(admin:dict,claim_id:int,decision:str,remark:str,path: str|Path=DB_PATH):
    if admin.get('role')!='admin': raise PermissionError("Only administrators can review claims.")
    if decision not in ('APPROVED','REJECTED'): raise ValueError("Choose approve or reject.")
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE"); claim=c.execute("SELECT c.*,i.status item_status,i.item_name FROM claims c JOIN items i ON i.id=c.item_id WHERE c.id=?",(claim_id,)).fetchone()
        if not claim or claim['status']!='PENDING' or claim['item_status']=='RETURNED': c.rollback(); raise ValueError("This claim is no longer pending.")
        if decision=='APPROVED' and c.execute("SELECT 1 FROM claims WHERE item_id=? AND status='APPROVED'",(claim['item_id'],)).fetchone(): c.rollback(); raise ValueError("Another claim for this item has already been approved.")
        c.execute("UPDATE claims SET status=?,admin_remark=?,reviewed_by=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=?",(decision,remark.strip(),admin['id'],claim_id))
        if decision=='APPROVED':
            competing=c.execute("SELECT claimant_id FROM claims WHERE item_id=? AND id<>? AND status='PENDING'",(claim['item_id'],claim_id)).fetchall()
            c.execute("UPDATE claims SET status='REJECTED',admin_remark='Another claim was approved.',reviewed_by=?,reviewed_at=CURRENT_TIMESTAMP WHERE item_id=? AND id<>? AND status='PENDING'",(admin['id'],claim['item_id'],claim_id))
            for other in competing:c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(other['claimant_id'],'Claim rejected','Another claim for this item was approved.'))
        elif not c.execute("SELECT 1 FROM claims WHERE item_id=? AND status='PENDING'",(claim['item_id'],)).fetchone():
            c.execute("UPDATE items SET status='OPEN' WHERE id=? AND status='IN_REVIEW'",(claim['item_id'],))
        c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(claim['claimant_id'],'Claim '+decision.lower(),remark.strip() or f"Your claim for {claim['item_name']} was {decision.lower()}."))
        c.commit()
def mark_returned(admin:dict,item_id:int,path: str|Path=DB_PATH):
    if admin.get('role')!='admin': raise PermissionError("Only administrators can mark an item returned.")
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE"); item=c.execute("SELECT item_name,owner_id FROM items WHERE id=?",(item_id,)).fetchone()
        if not item: c.rollback(); raise ValueError("Item not found.")
        c.execute("UPDATE items SET status='RETURNED' WHERE id=?",(item_id,))
        body=f"{item['item_name']} has been marked returned."
        c.execute("INSERT INTO notifications(user_id,title,body) VALUES(?,?,?)",(item['owner_id'],'Item returned',body))
        c.execute("INSERT INTO notifications(user_id,title,body) SELECT claimant_id,'Item returned',? FROM claims WHERE item_id=? AND status='APPROVED'",(body,item_id));c.commit()
def notifications(user_id:int,path: str|Path=DB_PATH):
    with connect(path) as c:return [dict(r) for r in c.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 30",(user_id,))]
