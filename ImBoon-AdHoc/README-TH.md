# อิ่มบุญ — โปรเจกต์ iPhone สำหรับ Ad Hoc

ไฟล์ชุดนี้เป็นซอร์สโปรเจกต์ Xcode ยังไม่ใช่ IPA และยังไม่มีลิงก์ติดตั้งจริง

เตรียมบทสวด 48 บท 12 หมวด พร้อมวิธีสวด ตัวหนังสือกึ่งกลาง ปรับขนาด บทโปรด โหมดกลางคืน และปัดเปลี่ยนบทไว้ในตัวแอปแล้ว เปิดอ่านบทสวดได้โดยไม่ต้องใช้อินเทอร์เน็ต ส่วนลิงก์แหล่งอ้างอิงต้องใช้อินเทอร์เน็ต การเพิ่มบทสวดในเว็บภายหลังจะไม่เข้ามาในแอปอัตโนมัติ ต้องสร้างเวอร์ชันใหม่

## สิ่งที่ต้องมี

1. Mac ที่ติดตั้ง Xcode 16 ขึ้นไป และ iOS SDK
2. บัญชี Apple Developer Program ที่ยังมีสมาชิกภาพ มีสิทธิ์สร้าง App ID, distribution certificate และ profile
3. UDID ของ iPhone ทุกเครื่องที่จะติดตั้ง แล้วลงทะเบียนเครื่องในบัญชีนักพัฒนา
4. ที่อยู่ HTTPS สำหรับแจก IPA และ manifest ซึ่งผู้รับโหลดได้โดยไม่ติดหน้าเข้าสู่ระบบ

ผู้รับไม่ต้องมีบัญชีนักพัฒนา แต่เครื่องต้องอยู่ในรายการของ profile ก่อน ตัวแอปและ profile มีอายุ ไม่ใช่การแจกถาวร ต้องดูวันหมดอายุจริงจากชุดที่เซ็นแล้ว เพิ่มเครื่องใหม่ภายหลังต้องสร้าง profile และส่ง IPA ชุดใหม่

## วิธีง่ายที่สุดบน Mac

1. แตก ZIP แล้วเปิด `ImBoon.xcodeproj`
2. เปิด Settings ของ Xcode → Accounts แล้วเพิ่มบัญชี Apple ของคุณเอง
3. เลือก Target `ImBoon` → Signing & Capabilities → เลือก Team และเปิด Automatically manage signing
4. ใช้ Bundle Identifier `com.tanat.imboon` หรือเปลี่ยนเป็น App ID ที่คุณเป็นเจ้าของ หากชื่อนี้ถูกใช้แล้ว
5. ลงทะเบียน UDID ของผู้รับใน Apple Developer → Certificates, Identifiers & Profiles → Devices
6. ลอง Run บน iPhone จริงก่อน ตรวจบทสวด การปัด การปรับขนาด บันทึกบทโปรด และทดสอบโหมดเครื่องบิน
7. เลือก Any iOS Device (arm64) แล้ว Product → Archive
8. ใน Organizer เลือก Distribute App → Custom → Release Testing / Ad Hoc (ชื่อขึ้นกับ Xcode) เลือกเครื่องที่ลงทะเบียนให้ครบ แล้ว Export เป็น IPA
9. ตรวจวันหมดอายุและรายการเครื่องของ profile อย่าเลือก Development หรือ App Store distribution

ต้องทำขั้นตอน Archive และลงลายเซ็นบน Mac โปรเจกต์นี้ยังไม่ได้ผ่านการคอมไพล์ด้วย Xcode หรือทดสอบบน iPhone จริง

## สร้างหน้าลิงก์ติดตั้ง หลังได้ IPA แล้ว

บน Mac รันคำสั่งนี้ โดยเปลี่ยนตำแหน่ง IPA และ URL ให้เป็นของจริง:

```bash
python3 distribution/make_install_page.py \
  --ipa /absolute/path/ImBoon.ipa \
  --base-url https://YOUR-HOST/im-boon \
  --output install-page
```

เครื่องมือจะตรวจว่า profile เป็นแบบ Ad Hoc มีเครื่องลงทะเบียนและยังไม่หมดอายุ แล้วสร้าง `index.html`, `manifest.plist` และสำเนา `ImBoon.ipa` โดยยังไม่อัปโหลดอะไร นำทั้ง 3 ไฟล์ไปไว้ที่ URL ที่กำหนด แล้วเปิดหน้าติดตั้งด้วย Safari ของ iPhone ที่ลงทะเบียน จากนั้นทดสอบติดตั้งจริงก่อนส่งให้ผู้รับคนอื่น

เว็บแอปอิ่มบุญเดิมยังเป็นส่วนตัว ไม่ควรใช้หน้าเข้าสู่ระบบเดิมเป็น URL แจก IPA ต้องมีปลายทาง HTTPS ที่โหลด IPA และ manifest ได้โดยตรง การใช้ Ad Hoc จำกัดด้วยรายชื่อเครื่อง ไม่ได้ทำให้ไฟล์ IPA เป็นข้อมูลลับบนหน้าแจก

## สำหรับผู้พัฒนาที่ใช้คำสั่ง build

```bash
export IMBOON_TEAM_ID='YOUR_APPLE_TEAM_ID'
# ถ้าใช้ Bundle ID ของตนเอง:
export IMBOON_BUNDLE_ID='com.yourcompany.imboon'
./distribution/build_adhoc.sh
```

Xcode ต้องลงชื่อเข้าใช้บัญชีและมีสิทธิ์จัดการ certificate/profile อยู่ก่อน สคริปต์ใช้ `release-testing` สำหรับ Xcode 16+ ไม่เก็บรหัสผ่านหรือ private key ในซอร์ส

## ตรวจแล้ว / ยังต้องตรวจ

ตรวจซอร์สบทสวดและวิธีสวด 48 บท การอ้างอิงไฟล์ในเครื่อง รูปไอคอน plist/XML และตรรกะหน้าแจกแล้ว ยังไม่ได้ build, archive, code-sign หรือทดสอบลิงก์ OTA จริง ไม่มีไฟล์ IPA ที่ติดตั้งได้ในชุดนี้

บทโปรดและการตั้งค่าของเว็บเดิมจะไม่ย้ายเข้ามาในแอปโดยอัตโนมัติ แอปเวอร์ชันนี้เก็บในเครื่อง ไม่ส่งข้อมูลไปเซิร์ฟเวอร์ ผู้ใช้กดลิงก์อ้างอิงจะเปิดเบราว์เซอร์ของระบบ

## อ้างอิง Apple

- https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile
- https://developer.apple.com/help/account/devices/devices-overview
- https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices
