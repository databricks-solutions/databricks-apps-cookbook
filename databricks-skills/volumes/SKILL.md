---
name: cookbook-volumes
description: "Upload and download files from Unity Catalog Volumes in Databricks Apps. Use when the user needs file upload, file download, or file management with UC Volumes in Dash, Streamlit, Reflex, or FastAPI."
---

# Unity Catalog Volumes

Upload and download files from [Unity Catalog Volumes](https://docs.databricks.com/en/volumes/index.html) using the Databricks SDK. Unlike notebooks, Databricks Apps cannot mount volumes directly -- files must be uploaded/downloaded via the SDK.

## Recipes

### Upload a file

#### Dash

```python
import io
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

with open("local_file.csv", "rb") as f:
    file_bytes = f.read()
binary_data = io.BytesIO(file_bytes)

volume_file_path = "/Volumes/catalog/schema/volume_name/local_file.csv"
w.files.upload(volume_file_path, binary_data, overwrite=True)
```

#### Streamlit

```python
import io
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

uploaded_file = st.file_uploader("Select file")
volume_path = st.text_input(
    "Volume path (catalog.schema.volume):",
    placeholder="main.marketing.raw_files",
)

if st.button("Upload") and uploaded_file and volume_path:
    binary_data = io.BytesIO(uploaded_file.read())
    parts = volume_path.strip().split(".")
    path = f"/Volumes/{parts[0]}/{parts[1]}/{parts[2]}/{uploaded_file.name}"
    w.files.upload(path, binary_data, overwrite=True)
    st.success(f"Uploaded to {path}")
```

#### Reflex

```python
import io
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class VolumeUploadState(rx.State):
    volume_path: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            parts = self.volume_path.strip().split(".")
            path = f"/Volumes/{parts[0]}/{parts[1]}/{parts[2]}/{file.filename}"
            w.files.upload(path, io.BytesIO(data), overwrite=True)
```

#### FastAPI

FastAPI uses OAuth client credentials to access the Files API for streaming:

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from databricks.sdk import WorkspaceClient

router = APIRouter()
w = WorkspaceClient()

@router.get("/files/{file_path:path}")
async def stream_file(file_path: str):
    response = w.files.download(f"/Volumes/{file_path}")
    return StreamingResponse(response.contents, media_type="application/octet-stream")
```

### Download a file

#### Dash / Streamlit / Reflex (common pattern)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

file_path = "/Volumes/catalog/schema/volume_name/file.csv"
response = w.files.download(file_path)
file_data = response.contents.read()
```

For Streamlit, use `st.download_button` to offer the file to the user:

```python
import streamlit as st

st.download_button(
    label="Download file",
    data=file_data,
    file_name="file.csv",
)
```

## Volume Path Format

Volumes use the path format: `/Volumes/<catalog>/<schema>/<volume_name>/<file_path>`

From a three-level name like `main.marketing.raw_files`:

```python
parts = "main.marketing.raw_files".split(".")
path = f"/Volumes/{parts[0]}/{parts[1]}/{parts[2]}/my_file.csv"
# -> /Volumes/main/marketing/raw_files/my_file.csv
```

## Resources

- [Unity Catalog Volume](https://docs.databricks.com/aws/en/files/volumes)

## Permissions

| Action | Permissions |
|--------|-----------|
| Upload | `USE CATALOG`, `USE SCHEMA`, `READ VOLUME`, `WRITE VOLUME` |
| Download | `USE CATALOG`, `USE SCHEMA`, `READ VOLUME` |

See [Volume operation privileges](https://docs.databricks.com/en/volumes/privileges.html#privileges-required-for-volume-operations).

## Dependencies

```
databricks-sdk
```

Plus your framework package (`dash`, `streamlit`, `reflex`, or `fastapi`).
