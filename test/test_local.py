import pypsql
from pathlib import Path

sql_script = """
SELECT *
FROM netflix_shows
"""

# local connection
conn = pypsql.DatabaseConnector(
    db_credential_file='.env_local'
)

df = conn.get_data(sql_script)
print(df)
