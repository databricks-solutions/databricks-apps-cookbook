import base64
import streamlit as st
from databricks.sdk import WorkspaceClient


w = WorkspaceClient()


def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode("utf-8")
        return decoded_secret
    except Exception as e:
        st.error(
            "Secret not found or inaccessible. Please create a secret scope and key before retrieving."
        )


st.header("External services", divider=True)
st.subheader("Retrieve a secret")
st.write(
    "This recipe retrieves a [Databricks secret](https://docs.databricks.com/en/security/secrets/index.html). Use secrets to securely connect to external services and APIs."
)

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    scope_name = st.text_input("Secret scope", placeholder="apis")
    secret_key = st.text_input("Secret key", placeholder="weather_service_key")

    if st.button("Retrieve"):
        secret = get_secret(scope_name, secret_key)
        st.success("Secret retrieved! The value is securely handled in the backend.")


with tab_b:
    st.code("""
    import streamlit as st
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()

    def get_secret(scope, key):
        try:
            secret_response = w.secrets.get_secret(scope=scope, key=key)
            decoded_secret = base64.b64decode(secret_response.value).decode('utf-8')
            return decoded_secret
        except Exception as e:
            st.error("Secret not found or inaccessible. Please create a secret scope and key before retrieving.")

    scope_name = st.text_input("Secret scope:", "my_secret_scope")
    secret_key = st.text_input("Secret key (name):", "api_key")

    if st.button("Retrieve"):
        secret = get_secret(scope_name, secret_key)
        st.success("Secret retrieved! The value is securely handled in the backend.")
    """)

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `CAN READ` on the secret scope
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Secret scope
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
