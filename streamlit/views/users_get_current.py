import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.iam import User

st.header(body="Users", divider=True)
st.subheader("Get current user")
st.write(
    "This recipe gets information about the user accessing this Databricks App from their [HTTP headers](https://docs.databricks.com/en/dev-tools/databricks-apps/app-development.html#what-http-headers-are-passed-to-databricks-apps)."
)

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    st.info(
        "For this sample to work when running on your local machine, use the `databricks apps run-local` CLI command which injects the necessary HTTP headers.",
        icon="ℹ️",
    )

    headers = st.context.headers

    user_access_token = headers.get("X-Forwarded-Access-Token")

    st.markdown(
        f"""
        #### Information extracted from HTTP headers

        E-mail: `{headers.get("X-Forwarded-Email")}`
        
        Username: `{headers.get("X-Forwarded-Preferred-Username")}`

        IP Address: `{headers.get("X-Real-Ip")}`

        X-Forwarded-Access-Token present: {"✅" if user_access_token else "❌"}
        """
    )

    st.markdown("**All headers**")

    st.json(headers.to_dict(), expanded=False)

    w = WorkspaceClient(token=user_access_token, auth_type="pat")

    current_user = w.current_user.me()

    print(current_user)

    st.markdown(
        "#### Information extracted from [`w.current_user.me()`](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/iam/current_user.html)"
    )

    st.info(
        "Enable [on-behalf-of-user authentication](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development#-using-the-databricks-apps-authorization-model) for this app to see information about the user visiting the app. Otherwise, this will display information about the app service principal.",
        icon="ℹ️",
    )

    st.markdown(
        f"""

        User ID: `{current_user.id}`
        
        Username: `{current_user.user_name}`
        
        Display Name: `{current_user.display_name}`
        
        Active: `{current_user.active}`
        
        Groups: `{len(current_user.groups) if current_user.groups else 0} groups`
        
        Entitlements: `{len(current_user.entitlements) if current_user.entitlements else 0} entitlements`
        
        """
    )

    st.markdown("**Full user object**")

    st.json(current_user.as_dict(), expanded=False)

with tab_b:
    st.code(
        """
        import streamlit as st
        from databricks.sdk import WorkspaceClient

        # Get information from HTTP headers
        headers = st.context.headers
        email = headers.get("X-Forwarded-Email")
        username = headers.get("X-Forwarded-Preferred-Username")
        user  = headers.get("X-Forwarded-User")
        ip = headers.get("X-Real-Ip")
        user_access_token = headers.get("X-Forwarded-Access-Token")

        # Display basic header information
        st.markdown(f"**User Information from Headers**")
        st.markdown(f"E-mail: `{email}`")
        st.markdown(f"Username: `{username}`")
        st.markdown(f"IP Address: `{ip}`")
        st.markdown(f"Access Token Available: {'✅' if user_access_token else '❌'}")

        # If we have a user access token, get detailed user information
        if user_access_token:
            # Initialize WorkspaceClient with the user's token
            w = WorkspaceClient(token=user_access_token, auth_type="pat")
            
            # Get current user information
            try:
                current_user = w.current_user.me()
                
                # Display detailed user information
                st.markdown("**User Information from API**")
                st.markdown(f"User ID: `{current_user.id}`")
                st.markdown(f"Username: `{current_user.user_name}`")
                st.markdown(f"Display Name: `{current_user.display_name}`")
                st.markdown(f"Active: `{current_user.active}`")
                
                # Show groups and entitlements if available
                if current_user.groups:
                    st.markdown(f"Groups: `{len(current_user.groups)} groups`")
                
                if current_user.entitlements:
                    st.markdown(f"Entitlements: `{len(current_user.entitlements)} entitlements`")
                
                # Display the full user object as JSON
                st.json(current_user.as_dict())
            except Exception as e:
                st.error(f"Error accessing user details: {str(e)}")
        """
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions**

                    No permissions configuration required for accessing headers. To use the `current_user.me()` API, the app must be configured with on-behalf-of-user authentication.
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                   
                    None
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks`
                    """)
