#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v xcodebuild >/dev/null 2>&1; then
  echo 'ต้องรันบน Mac ที่ติดตั้ง Xcode แล้ว' >&2
  exit 1
fi
: "${IMBOON_TEAM_ID:?ตั้ง IMBOON_TEAM_ID เป็น Team ID ของบัญชี Apple Developer ก่อน}"
IMBOON_BUNDLE_ID="${IMBOON_BUNDLE_ID:-com.tanat.imboon}"
mkdir -p build
xcodebuild -project ImBoon.xcodeproj -scheme ImBoon -configuration Release \
  -destination 'generic/platform=iOS' -archivePath build/ImBoon.xcarchive \
  -allowProvisioningUpdates DEVELOPMENT_TEAM="$IMBOON_TEAM_ID" \
  PRODUCT_BUNDLE_IDENTIFIER="$IMBOON_BUNDLE_ID" CODE_SIGN_STYLE=Automatic archive
/usr/bin/python3 - "$IMBOON_TEAM_ID" <<'PY'
import plistlib,sys
with open('build/ExportOptions.plist','wb') as f:
 plistlib.dump({'method':'release-testing','signingStyle':'automatic','teamID':sys.argv[1],
  'manageAppVersionAndBuildNumber':False,'thinning':'<none>'},f)
PY
xcodebuild -exportArchive -archivePath build/ImBoon.xcarchive \
  -exportPath build/export -exportOptionsPlist build/ExportOptions.plist -allowProvisioningUpdates
printf '\nไฟล์แอปที่ Export อยู่ใน build/export\n'
