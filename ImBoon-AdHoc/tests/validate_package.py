from pathlib import Path
import re,json,plistlib,xml.etree.ElementTree as ET,importlib.util,tempfile,zipfile,datetime,subprocess
import struct
root=Path(__file__).resolve().parents[1]
# Parse the OpenStep project syntax without needing Apple's build toolchain.
text=(root/'ImBoon.xcodeproj/project.pbxproj').read_text();text=re.sub(r'//[^\n]*','',text)
tokens=re.findall(r'"(?:\\.|[^"\\])*"|[{}()=;,]|[^\s{}()=;,]+',text);i=0
def atom():
 global i
 t=tokens[i];i+=1
 if t=='{':
  d={}
  while tokens[i]!='}':
   key=atom();assert tokens[i]=='=';i+=1;d[key]=atom();assert tokens[i]==';';i+=1
  i+=1;return d
 if t=='(':
  a=[]
  while tokens[i]!=')':
   a.append(atom())
   if tokens[i]==',':i+=1
  i+=1;return a
 return json.loads(t) if t.startswith('"') else t
proj=atom();assert i==len(tokens);objects=proj['objects'];assert proj['rootObject'] in objects
for ref in re.findall(r'\bA[0-9A-F]{23}\b',text):assert ref in objects,ref
assert objects['A0000000000000000000000F']['lastKnownFileType']=='folder'
ET.parse(root/'ImBoon.xcodeproj/xcshareddata/xcschemes/ImBoon.xcscheme')
for p in (root/'ImBoon').glob('*.plist'):plistlib.loads(p.read_bytes())
plistlib.loads((root/'ImBoon/PrivacyInfo.xcprivacy').read_bytes())
for p in (root/'ImBoon/Assets.xcassets').rglob('Contents.json'):json.loads(p.read_text())
for p in (root/'ImBoon/Assets.xcassets/AppIcon.appiconset').glob('*.png'):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',b[16:24]);assert w==h and b[25]==2
h=(root/'ImBoon/Web/index.html').read_text();assert 'src="prayers.js"' in h and 'src="/prayers.js"' not in h and '.chant{text-align:center' in h
assert 'https://tanat-prayer-book' not in h
spec=importlib.util.spec_from_file_location('install',root/'distribution/make_install_page.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);info={'CFBundleIdentifier':'com.tanat.imboon','CFBundleVersion':'1','CFBundleDisplayName':'อิ่มบุญ'}
 def ipa(name,signed):
  p=tmp/name
  with zipfile.ZipFile(p,'w') as z:
   z.writestr('Payload/ImBoon.app/Info.plist',plistlib.dumps(info))
   if signed:z.writestr('Payload/ImBoon.app/embedded.mobileprovision',b'TEST');z.writestr('Payload/ImBoon.app/_CodeSignature/CodeResources',b'TEST')
  return p
 unsigned=ipa('unsigned.ipa',False);signed=ipa('signed-mock.ipa',True)
 try:mod.make_page(unsigned,'https://example.com/install',tmp/'out');raise AssertionError('Unsigned IPA accepted')
 except ValueError as e:assert 'ลายเซ็น' in str(e)
 profile={'ProvisionedDevices':['TEST-DEVICE'],'Entitlements':{'application-identifier':'TEAM.com.tanat.imboon','get-task-allow':False},'ExpirationDate':datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)+datetime.timedelta(days=30)}
 class Result:stdout=plistlib.dumps(profile)
 original=mod.subprocess.run;mod.subprocess.run=lambda *a,**kw:Result()
 mod.make_page(signed,'https://example.com/install',tmp/'out')
 manifest=plistlib.loads((tmp/'out/manifest.plist').read_bytes());assert manifest['items'][0]['assets'][0]['url']=='https://example.com/install/ImBoon.ipa'
 assert 'itms-services://' in (tmp/'out/index.html').read_text()
 profile['Entitlements']['get-task-allow']=True;Result.stdout=plistlib.dumps(profile)
 try:mod.make_page(signed,'https://example.com/install',tmp/'no');raise AssertionError('Development profile accepted')
 except ValueError:pass
 mod.subprocess.run=original
print('Passed source/package structure and signed-IPA download-page safeguards using mocked profiles. No native build/signing performed.')
