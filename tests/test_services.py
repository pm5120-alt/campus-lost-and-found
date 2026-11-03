import tempfile,unittest
import os
from unittest.mock import patch
from pathlib import Path
import database
from matching import explain_match

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'test.sqlite3';database.setup_database(self.db)
        self.student=database.register('student_one','strongpassword123',path=self.db)
        self.other=database.register('student_two','anotherpassword123',path=self.db)
        # Test-only administrator creation mirrors secure salted credential storage.
        import secrets
        salt=secrets.token_bytes(16)
        with database.connect(self.db) as c:c.execute("INSERT INTO users(username,password_hash,salt,role) VALUES(?,?,?,'admin')",('admin',database._password('adminpassword123',salt).hex(),salt.hex()))
        self.admin=database.authenticate('admin','adminpassword123',self.db)
    def tearDown(self):self.tmp.cleanup()
    def item(self,owner,kind,name='Blue wallet'):
        return database.create_item(owner,{'type':kind,'item_name':name,'category':'Accessories','description':'blue leather wallet with campus card','location':'Library','event_date':'2026-10-30'},self.db)
    def test_auth_hash_duplicate_and_student_role(self):
        self.assertIsNotNone(database.authenticate('student_one','strongpassword123',self.db));self.assertIsNone(database.authenticate('student_one','wrongpassword',self.db))
        with self.assertRaises(ValueError):database.register('student_one','strongpassword123',path=self.db)
        with self.assertRaises(PermissionError):database.register('fake_admin','strongpassword123',role='admin',path=self.db)
    def test_admin_setup_requires_environment_secret_and_is_one_time(self):
        path=Path(self.tmp.name)/'admin-setup.sqlite3';database.setup_database(path)
        with self.assertRaises(PermissionError):database.bootstrap_admin('operator','securepassword123','wrong-code',path)
        token='setup-secret-with-more-than-24-characters'
        with patch.dict(os.environ,{'CAMPUS_ADMIN_SETUP_TOKEN':token}):
            admin_id=database.bootstrap_admin('operator','securepassword123',token,path)
            self.assertEqual(database.authenticate('operator','securepassword123',path)['role'],'admin')
            with self.assertRaises(PermissionError):database.bootstrap_admin('second','securepassword456',token,path)
    def test_items_search_and_owner_isolation(self):
        iid=self.item(self.student,'lost');self.item(self.other,'found')
        self.assertEqual(len(database.search_items({'keyword':'wallet','category':'Accessories'},path=self.db)),2)
        self.assertEqual([x['id'] for x in database.my_items(self.student,self.db)],[iid])
    def test_claim_review_and_notifications(self):
        iid=self.item(self.other,'found');cid=database.create_claim(iid,self.student,'There is a hidden scratch under the flap.',self.db)
        student=database.authenticate('student_one','strongpassword123',self.db)
        self.assertEqual(database.list_claims(student,self.db)[0]['evidence'],'There is a hidden scratch under the flap.')
        with self.assertRaises(PermissionError):database.review_claim({'id':self.student,'role':'student'},cid,'APPROVED','',self.db)
        database.review_claim(self.admin,cid,'APPROVED','Verified at desk.',self.db)
        self.assertEqual(database.list_claims(student,self.db)[0]['status'],'APPROVED')
        self.assertTrue(database.notifications(self.student,self.db))
        database.mark_returned(self.admin,iid,self.db);self.assertEqual(database.counts(self.db)['returned'],1)
    def test_claim_conflict_and_rejection(self):
        iid=self.item(self.other,'found');a=database.create_claim(iid,self.student,'Unique proof one',self.db)
        self.assertIsNotNone(a)
        with self.assertRaises(ValueError):database.create_claim(iid,self.student,'Unique proof two',self.db)
        database.review_claim(self.admin,a,'REJECTED','More evidence is needed.',self.db)
        self.assertEqual(database.list_claims(self.admin,self.db)[0]['status'],'REJECTED')
    def test_matching_explains_score(self):
        a={'type':'lost','category':'Accessories','item_name':'Blue wallet','description':'blue leather wallet','location':'Library','event_date':'2026-10-30'}
        b={'type':'found','category':'Accessories','item_name':'Blue wallet','description':'blue leather wallet with card','location':'Library','event_date':'2026-10-31'}
        result=explain_match(a,b);self.assertGreaterEqual(result['score'],80);self.assertTrue(result['reasons'])
    def test_validation_and_admin_approval_conflict(self):
        with self.assertRaises(ValueError):self.item(self.student,'lost','')
        item=self.item(self.other,'found');claim=database.create_claim(item,self.student,'my unique identifying mark',self.db);database.review_claim(self.admin,claim,'APPROVED','Verified.',self.db)
        with self.assertRaises(ValueError):database.create_claim(item,self.student,'second claim',self.db)

    def test_potential_match_notice_and_conflicting_claim_resolution(self):
        found=self.item(self.admin['id'],'found');lost=self.item(self.student,'lost')
        self.assertEqual(database.counts(self.db)['lost'],1)
        self.assertTrue(any(n['title']=='Potential item match' for n in database.notifications(self.student,self.db)))
        # Two distinct students may submit evidence, but one approval closes the other.
        first=database.create_claim(found,self.student,'Small nick on the underside',self.db)
        second=database.create_claim(found,self.other,'Blue stitching on the inner seam',self.db)
        database.review_claim(self.admin,first,'APPROVED','Identity verified.',self.db)
        claims=database.list_claims(self.admin,self.db)
        self.assertEqual(sum(c['status']=='APPROVED' for c in claims),1)
        self.assertTrue(any(c['id']==second and c['status']=='REJECTED' for c in claims))
        self.assertTrue(any(n['title']=='Claim rejected' for n in database.notifications(self.other,self.db)))

if __name__=='__main__':unittest.main()
