"""Create a download page ONLY from an already signed Ad Hoc IPA. Does not upload."""
import argparse,datetime,html,plistlib,shutil,subprocess,tempfile,zipfile
from pathlib import Path
from urllib.parse import urlparse,quote

def make_page(ipa,base,out):
 if urlparse(base).scheme!='https' or not urlparse(base).hostname:
  raise ValueError('ต้องใช้ base URL แบบ HTTPS ที่ผู้รับเข้าถึงได้โดยไม่ต้องล็อกอิน')
 if urlparse(base).query or urlparse(base).fragment:
  raise ValueError('base URL ต้องไม่มี query หรือ fragment')
 out=Path(out);ipa=Path(ipa)
 if out.resolve() in ipa.resolve().parents:
  raise ValueError('ให้วาง IPA ต้นทางนอกโฟลเดอร์ output')
 with zipfile.ZipFile(ipa) as z:
  names=z.namelist();infos=[n for n in names if n.startswith('Payload/') and n.count('/')==2 and n.endswith('.app/Info.plist')]
  if len(infos)!=1:raise ValueError('ไม่พบแอปหลักเพียงหนึ่งแอปใน IPA')
  prefix=infos[0].rsplit('/',1)[0]+'/';info=plistlib.loads(z.read(infos[0]))
  if prefix+'embedded.mobileprovision' not in names or prefix+'_CodeSignature/CodeResources' not in names:
   raise ValueError('IPA นี้ยังไม่มี profile และลายเซ็นครบ ให้ Export แบบ Ad Hoc จาก Xcode ก่อน')
  with tempfile.TemporaryDirectory() as tmp:
   profile=Path(tmp)/'profile.mobileprovision';profile.write_bytes(z.read(prefix+'embedded.mobileprovision'))
   try:decoded=subprocess.run(['security','cms','-D','-i',str(profile)],check=True,capture_output=True).stdout
   except (FileNotFoundError,subprocess.CalledProcessError) as error:
    raise ValueError('ต้องตรวจ profile ด้วยเครื่องมือ security บน Mac') from error
   profile_data=plistlib.loads(decoded)
  devices=profile_data.get('ProvisionedDevices',[]);ent=profile_data.get('Entitlements',{})
  if not devices or profile_data.get('ProvisionsAllDevices') or ent.get('get-task-allow',False):
   raise ValueError('profile ต้องเป็น Ad Hoc สำหรับเครื่องที่ลงทะเบียน ไม่ใช่ Development หรือ Enterprise')
  expires=profile_data.get('ExpirationDate')
  if not expires or expires.replace(tzinfo=datetime.timezone.utc)<=datetime.datetime.now(datetime.timezone.utc):
   raise ValueError('profile หมดอายุหรือไม่พบวันหมดอายุ')
  bundle=info['CFBundleIdentifier'];app_id=ent.get('application-identifier','')
  if not (app_id.endswith('.'+bundle) or app_id.endswith('.*')):raise ValueError('Bundle ID ไม่ตรงกับ profile')
  version=str(info['CFBundleVersion']);title=info.get('CFBundleDisplayName','อิ่มบุญ')
 out.mkdir(parents=True,exist_ok=True);shutil.copy2(ipa,out/'ImBoon.ipa');base=base.rstrip('/')
 manifest={'items':[{'assets':[{'kind':'software-package','url':base+'/ImBoon.ipa'}],'metadata':{'bundle-identifier':bundle,'bundle-version':version,'kind':'software','title':title}}]}
 (out/'manifest.plist').write_bytes(plistlib.dumps(manifest))
 install='itms-services://?action=download-manifest&url='+quote(base+'/manifest.plist',safe='')
 (out/'index.html').write_text('<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' — ติดตั้ง</title><style>body{background:#f7f5ef;color:#263c32;font:18px system-ui;max-width:520px;margin:60px auto;padding:24px;line-height:1.9}a{display:block;background:#395747;color:white;border-radius:16px;text-align:center;padding:14px;text-decoration:none}</style><h1>'+html.escape(title)+'</h1><p>แอปบทสวดมนต์สำหรับ iPhone</p><a href="'+html.escape(install,quote=True)+'">ติดตั้งแอปอิ่มบุญ</a><p>เปิดหน้านี้ใน Safari บน iPhone ที่ลงทะเบียน UDID ไว้แล้ว และกดติดตั้ง จากนั้นกลับไปดูไอคอนบนหน้าจอโฮม</p><p>ติดตั้งได้เฉพาะเครื่องที่อยู่ใน profile ของไฟล์นี้ ลิงก์นี้ไม่ได้ลงทะเบียนเครื่องให้อัตโนมัติ</p><p>สิทธิ์การติดตั้งของชุดนี้หมดอายุ '+expires.date().isoformat()+' ต้องส่งไฟล์ที่ลงนามใหม่ก่อนหมดอายุ</p></html>',encoding='utf-8')
 print('สร้างหน้าและไฟล์แจกแล้ว:',out,'เครื่องที่ลงทะเบียน:',len(devices))
 print('ยังไม่ได้อัปโหลด ต้องนำทุกไฟล์ในโฟลเดอร์นี้ขึ้น HTTPS ก่อนส่งลิงก์')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True);p.add_argument('--base-url',required=True);p.add_argument('--output',default='install-page');a=p.parse_args()
 try:make_page(a.ipa,a.base_url,a.output)
 except (ValueError,KeyError,zipfile.BadZipFile) as error:p.exit(1,str(error)+'\n')
