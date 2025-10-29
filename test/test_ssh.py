from pypsql import SSHDatabaseConnector
from pathlib import Path

sql_script = """
SELECT *
FROM customers
"""

with SSHDatabaseConnector(
	ssh_port = 22,
	db_credential_file='.env_ssh'
) as ssh_db:    
	df = ssh_db.get_data(sql_script)
	print(df)