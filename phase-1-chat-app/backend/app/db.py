from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import settings

# Opened in main.py when the server starts, closed when it stops.
pool = AsyncConnectionPool(settings.database_url, open=False, kwargs={"row_factory": dict_row})