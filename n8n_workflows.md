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
6.  **AnythingLLM Node**: Index file content in relevant workspace.

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
