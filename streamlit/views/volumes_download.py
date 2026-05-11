import os
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

st.header(body="Volumes", divider=True)
st.subheader("Download a file")

st.write(
    "This recipe downloads a file from a [Unity Catalog volume](https://docs.databricks.com/en/volumes/index.html)."
)

tab1, tab2, tab3 = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab1:
    download_file_path = st.text_input(
        label="Specify a path to a file in a Unity Catalog volume:",
        placeholder="/Volumes/main/marketing/raw_files/leads.csv",
    )

    if st.button("Get file"):
        if download_file_path:
            try:
                resp = w.files.download(download_file_path)
                file_data = resp.contents.read()

                file_name = os.path.basename(download_file_path)

                st.success(f"File '{file_name}' downloaded successfully", icon="✅")
                st.download_button(
                    label="Download file",
                    data=file_data,
                    file_name=file_name,
                    mime="application/octet-stream",
                )
            except Exception as e:
                st.error(f"Error downloading file: {str(e)}")
        else:
            st.warning("Please specify a file path.")

with tab2:
    st.code("""
    import os
    import streamlit as st
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()

    download_file_path = st.text_input(
        label="Path to file", placeholder="/Volumes/catalog/schema/volume_name/file.csv"
    )

    response = w.files.download(download_file_path)
    file_data = response.contents.read()
    file_name = os.path.basename(download_file_path)

    st.download_button(label="Download", data=file_data, file_name=file_name)
    """)

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `USE CATALOG` on the volume's catalog
                    * `USE SCHEMA` on the volume's schema
                    * `READ VOLUME` on the volume

                    See [Privileges required for volume operations](https://docs.databricks.com/en/volumes/privileges.html#privileges-required-for-volume-operations) for more information.

                    If you declare volume access in a Databricks Asset Bundle, `resources.apps[*].resources[*].uc_securable` may not grant `USE_CATALOG` and `USE_SCHEMA` on the parent catalog and schema (the app still needs them at runtime). As a temporary workaround until bundles can declare those parent grants, add the privileges manually, or see [apps_grants_sync](https://github.com/salihbout/apps_grants_sync): an example Databricks App and Asset Bundle that wires `experimental.scripts.postdeploy` so parent privileges are applied after each `databricks bundle deploy` (copy its `tools/` into your bundle or mirror the same pattern in `databricks.yml`).

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
