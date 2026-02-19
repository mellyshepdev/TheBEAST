# n8n Workflow Templates for The Beast

These workflow definitions are required for the `cloud-storage` and `storage-optimizer` skills to function.

## 1. Beast-Cloud-Ingest (Learning)
**Trigger**: HTTP Request (from Agent) or Cron (Daily)
**Nodes**:
1.  **Google Drive Node**: List files in monitored folders.
2.  **OneDrive Node**: List files in monitored folders.
3.  **Filter**: New files since last run.
4.  **Metadata Extract**: AI Agent node or Code node to extract tags/summaries.
5.  **Supabase Node**: Upsert metadata into `public.cloud_files`.
6.  **AnythingLLM Node**: Index file content 
in relevant workspace.

## 2. Beast-Cloud-Fetch (Referencing)
**Trigger**: HTTP Request (from Agent)
**Nodes**:
1.  **Webhook Node**: Receives `file_id` and `provider`.
2.  **Switch**: Route to Google Drive or OneDrive.
3.  **Cloud Provider Node**: Download file content.
4.  **Response Node**: Return content to the Agent.

## 3. Beast-Cloud-Upload (Offloading)
**Trigger**: HTTP Request (from Agent/Storage Manager)
**Nodes**:
1.  **Webhook Node**: Receives file payload or path.
2.  **Cloud Provider Node**: Upload to `archives/` folder.
3.  **Validation**: Check size/hash in cloud vs source.
4.  **Response Node**: Return `success` and `cloud_url`.

## 4. Beast-Disk-Alert (Monitoring)
**Trigger**: `storage_manager.py` (via Webhook)
**Nodes**:
1.  **Webhook Node**: Receives disk pressure stats.
2.  **OpenClaw Node**: Route notification to User (Matrix/Slack/WhatsApp).
3.  **Agent Logic**: "I'm running out of space. Here is my plan..."

## 5. Beast-Content-Scout (Daily Pet Content Suggestions)
**Trigger**: Cron (Daily at 8:00 AM) or HTTP Request (manual: "What should Blue do today?")
**Nodes**:
1.  **Execute Command Node**: Run `python trend_scout.py --save --json` to fetch trends via Perplexity and generate today's suggestion.
2.  **Parse JSON Node**: Extract suggestion title, instructions, caption, hashtags, and timing.
3.  **OpenClaw Node**: Send the daily suggestion to Georg via Matrix/WhatsApp/Slack with the full creative brief.
4.  **Webhook Node (Wait)**: `Beast-Content-Upload` — waits for Georg to upload his photo/video after shooting.
5.  **Execute Command Node**: Run `python content_poster.py --media [uploaded_file] --platform all --from-suggestion` to post with today's trending hashtags.
6.  **OpenClaw Node**: Send confirmation with the live post link back to Georg.
7.  **Supabase Node**: Log the post record (date, platform, hashtags, engagement baseline) to `public.content_posts`.

## 6. Beast-SEO-Monitor (Daily SEO Health & Growth)
**Trigger**: Cron (Daily at 7:00 AM) or HTTP Request (manual: "How's my SEO?")
**Nodes**:
1.  **Execute Command Node**: Run `python seo_monitor.py --save --json` to audit the site.
2.  **Parse JSON Node**: Extract performance score, issues, and growth suggestions.
3.  **OpenClaw Node**: Send the daily SEO briefing to Georg via Matrix/WhatsApp/Slack.
4.  **Supabase Node**: Log the audit (date, performance score, issue count, top issues) to `public.seo_audits`.
5.  **Conditional Node**: If performance score drops below 60, trigger a HIGH PRIORITY alert.
