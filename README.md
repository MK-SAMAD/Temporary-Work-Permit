# Work Permit Tracker (website + WhatsApp alerts)

Files
- index.html: the website (search by Civil ID, sort by store)
- permits.xlsx: your data (keep the same 7 columns)
- notify.py + .github/workflows/permit-alerts.yml: daily WhatsApp alerts (today + 7 days before)

1. Get a WhatsApp API key (each person who should receive alerts does this once, from their own phone)
   - Open https://www.callmebot.com/blog/free-api-whatsapp-messages/ and copy the CURRENT bot phone number (it changes).
   - Save that number as a contact, then send it this WhatsApp message: I allow callmebot to send me messages
   - Wait up to 2 minutes. The bot replies with your API key.
2. Create a free GitHub account and a new repository. Upload ALL files, including the .github folder.
3. Website: Settings > Pages > Deploy from a branch > main / root > Save.
4. Settings > Secrets and variables > Actions > New repository secret:
   - Name: WHATSAPP_RECIPIENTS
   - Value: +965XXXXXXXX:YOURAPIKEY   (several people: +965AAA:key1,+965BBB:key2)
5. Actions tab > Permit alerts > Run workflow to test. It then runs by itself every day at 08:00 Kuwait time.
   (Test only sends if a permit expires today or in exactly 7 days.)

To update permits: upload a new permits.xlsx with the same name to the repository.
Optional email: also add secrets EMAIL_USER, EMAIL_PASS (Gmail app password), EMAIL_TO.

ADD / DELETE PERMITS FROM THE WEBSITE
1. GitHub > your profile picture > Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token.
2. Repository access: Only select repositories > choose permit-tracker. Permissions > Contents: Read and write. Generate and copy the token.
3. On your website open "Settings: connect GitHub", enter owner/repo-name and the token, press Save settings.
4. Use "+ Add permit". The permit is saved into permits.xlsx in your repository, and the WhatsApp alerts use it automatically.
Keep the token private. Anyone with it can edit your permits file.
