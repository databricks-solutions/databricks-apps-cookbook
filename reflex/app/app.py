import reflex_enterprise as rxe
import reflex as rx
import reflex_enterprise as rxe
from app.pages.introduction import introduction_page
from app.pages.oltp_database import oltp_database_page
from app.states.oltp_database_state import OltpDatabaseState
from app.pages.read_delta_table import read_delta_table_page
from app.pages.edit_delta_table import edit_delta_table_page
from app.pages.upload_file import upload_file_page
from app.pages.download_file import download_file_page
from app.pages.invoke_model import invoke_model_page
from app.pages.run_vector_search import run_vector_search_page
from app.pages.ai_bi_dashboard import ai_bi_dashboard_page
from app.pages.genie import genie_page
from app.pages.trigger_job import trigger_job_page
from app.pages.retrieve_job_results import retrieve_job_results_page
from app.pages.list_catalogs_schemas import list_catalogs_schemas_page
from app.pages.get_current_user import get_current_user_page
from app.pages.on_behalf_of_user import on_behalf_of_user_page
from app.pages.retrieve_a_secret import retrieve_a_secret_page
from app.pages.connect_cluster import connect_cluster_page
from app.pages.connect_mcp_server import connect_mcp_server_page
from app.pages.invoke_multimodal_llm import invoke_multimodal_llm_page
from app.pages.external_connections import external_connections_page
from app.states.edit_delta_table_state import EditDeltaTableState
from app.states.read_delta_table_state import ReadTableState
from app.states.invoke_model_state import InvokeModelState

index = introduction_page
app = rxe.App(theme=rx.theme(appearance="light"))
app.add_page(index, route="/")
app.add_page(introduction_page, route="/introduction")
app.add_page(
    oltp_database_page, route="/oltp-database", on_load=OltpDatabaseState.on_load
)
app.add_page(
    read_delta_table_page, route="/read-delta-table", on_load=ReadTableState.on_load
)
app.add_page(
    edit_delta_table_page,
    route="/edit-delta-table",
    on_load=EditDeltaTableState.on_load,
)
app.add_page(upload_file_page, route="/upload-file")
app.add_page(download_file_page, route="/download-file")
app.add_page(invoke_model_page, route="/invoke-model", on_load=InvokeModelState.on_load)
app.add_page(run_vector_search_page, route="/run-vector-search")
app.add_page(connect_mcp_server_page, route="/connect-mcp-server")
app.add_page(invoke_multimodal_llm_page, route="/invoke-multimodal-llm")
app.add_page(ai_bi_dashboard_page, route="/ai-bi-dashboard")
app.add_page(genie_page, route="/genie")
app.add_page(trigger_job_page, route="/trigger-job")
app.add_page(retrieve_job_results_page, route="/retrieve-job-results")
app.add_page(list_catalogs_schemas_page, route="/list-catalogs-schemas")
app.add_page(get_current_user_page, route="/get-current-user")
app.add_page(on_behalf_of_user_page, route="/on-behalf-of-user")
app.add_page(retrieve_a_secret_page, route="/retrieve-a-secret")
app.add_page(external_connections_page, route="/external-connections")
app.add_page(connect_cluster_page, route="/connect-cluster")