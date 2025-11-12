import os
import io
import streamlit as st
from databricks.sdk import WorkspaceClient


databricks_host = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_HOSTNAME")
w = WorkspaceClient()

st.header(body="Volumes", divider=True)
st.subheader("Upload a file")

st.write(
    "This recipe uploads a file to a [Unity Catalog Volume](https://docs.databricks.com/en/volumes/index.html)."
)

tab1, tab2, tab3 = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])


def check_upload_permissions(volume_name: str):
    try:
        volume = w.volumes.read(name=volume_name)
        current_user = w.current_user.me()
        grants = w.grants.get_effective(
            securable_type="volume",
            full_name=volume.full_name,
            principal=current_user.user_name,
        )

        if not grants or not grants.privilege_assignments:
            return "Insufficient permissions: No grants found."

        for assignment in grants.privilege_assignments:
            for privilege in assignment.privileges:
                if privilege.privilege.value in ["ALL_PRIVILEGES", "WRITE_VOLUME"]:
                    return "Volume and permissions validated"

        return "Insufficient permissions: Required privileges not found."
    except Exception as e:
        return f"Error: {e}"


if "volume_check_success" not in st.session_state:
    st.session_state.volume_check_success = False

with tab1:
    upload_volume_path = st.text_input(
        label="Specify a Unity Catalog Volume name:",
        placeholder="main.marketing.raw_files",
    )

    if st.button(label="Check Volume and permissions", icon=":material/lock_reset:"):
        permission_result = check_upload_permissions(upload_volume_path.strip())
        if permission_result == "Volume and permissions validated":
            st.session_state.volume_check_success = True
            st.success("Volume and permissions validated", icon="✅")
        else:
            st.session_state.volume_check_success = False
            st.error(permission_result, icon="🚨")

    if st.session_state.volume_check_success:
        uploaded_file = st.file_uploader(label="Pick a file to upload")

        if st.button(
            f"Upload file to {upload_volume_path}", icon=":material/upload_file:"
        ):
            if not upload_volume_path.strip():
                st.warning("Please specify a valid Volume path.", icon="⚠️")
            elif not uploaded_file:
                st.warning("Please pick a file to upload.", icon="⚠️")
            else:
                try:
                    file_bytes = uploaded_file.read()
                    binary_data = io.BytesIO(file_bytes)
                    file_name = uploaded_file.name
                    parts = upload_volume_path.strip().split(".")
                    catalog = parts[0]
                    schema = parts[1]
                    volume_name = parts[2]
                    volume_file_path = (
                        f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
                    )
                    w.files.upload(volume_file_path, binary_data, overwrite=True)
                    volume_url = f"https://{databricks_host}/explore/data/volumes/{catalog}/{schema}/{volume_name}"
                    st.success(
                        f"File '{file_name}' successfully uploaded to **{upload_volume_path}**. [Go to volume]({volume_url}).",
                        icon="✅",
                    )
                except Exception as e:
                    st.error(f"Error uploading file: {e}", icon="🚨")

with tab2:
    st.code("""
    import io
    import streamlit as st
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()

    uploaded_file = st.file_uploader(label="Select file")

    upload_volume_path = st.text_input(
        label="Specify a three-level Unity Catalog volume name (catalog.schema.volume_name)",
        placeholder="main.marketing.raw_files",
    )

    if st.button("Save changes"):
        file_bytes = uploaded_file.read()
        binary_data = io.BytesIO(file_bytes)
        file_name = uploaded_file.name
        parts = upload_volume_path.strip().split(".")
        catalog = parts[0]
        schema = parts[1]
        volume_name = parts[2]
        volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
        w.files.upload(volume_file_path, binary_data, overwrite=True)

    """)

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `USE CATALOG` on the catalog of the volume
                    * `USE SCHEMA` on the schema of the volume
                    * `READ VOLUME` and `WRITE VOLUME` on the volume

                    See [Privileges required for volume operations](https://docs.databricks.com/en/volumes/privileges.html#privileges-required-for-volume-operations) for more information. 

                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Unity Catalog volume
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
