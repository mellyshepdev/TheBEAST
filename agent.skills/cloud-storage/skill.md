---
name: Cloud Storage
description: Instructions for managing Google Drive and OneDrive access.
version: 1.0
owner: Georg
tags: [cloud, storage, google-drive, onedrive, backup]
allowed-tools: ["run_command", "view_file"]
---

# Cloud Storage Skills

## Philosophy

- **Cloud as Extension**: Treat cloud storage as an infinite extension of local storage.
- **Privacy First**: Only index files the user explicitly allows or those in "monitored" folders.
- **Sync, Don't Just Store**: Ensure metadata is indexed for search, even if the file is only in the cloud.

## Operations

### 1. Ingestion (Learning)
- **Tool**: Trigger n8n workflow `Beast-Cloud-Ingest`.
- **Process**:
    1. Scan for new files/photos.
    2. Extract metadata (date, location, tags, faces).
    3. Generate summary or vector embeddings for AnythingLLM/Supabase.
    4. Store reference URL in `public.cloud_files`.

### 2. Retrieval (Referencing)
- **Goal**: "What did I do in London last summer?"
- **Process**:
    1. Search Supabase for relevant metadata.
    2. If file content is needed, use n8n workflow `Beast-Cloud-Fetch` to download temp copy.
    3. Process and answer user.

### 3. Offloading (Archiving)
- **Trigger**: Called by `storage-optimizer` skill.
- **Process**:
    1. Receive list of local file paths.
    2. Upload to relevant cloud provider (Drive/OneDrive) using n8n.
    3. Verify integrity (compare hash or size).
    4. Return success status.

## Safety & Standards
- **Integrity**: Never delete a local file until cloud storage is confirmed.
- **Bandwidth**: Perform large uploads during off-peak hours (configured by user).
- **Format**: Prefer non-proprietary formats for archives (e.g., `.zip` or `.tar.gz`).
