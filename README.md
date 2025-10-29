# pypSQL


<a href="https://www.marius-liebald.com/pypsql/index.html" style="float:right; margin-left:10px;">
<img src="docs/source/_static/img/pypsql_logo_dark.png" style="height:139px !important; width:auto !important;" alt="pypsql utilities website" />
</a>

<!-- badges: start -->

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
<!-- badges: end -->

`pypsql` is a lightweight framework for connecting to PostgreSQL
databases, whether locally or remotely hosted. It builds on top of
[`SQLAlchemy`](https://www.sqlalchemy.org/) to provide a simple,
Pythonic interface for establishing connections, running queries, and
managing database sessions.

# Contributors

[Marius Liebald](https://www.marius-liebald.de) (maintainer)

# Installation

``` bash
pip install pypsql
```

# Usage

## Local Usage

### Provide database credentials

You can store the database connection details in a file, for example
`.env`:

``` python
SERVER=<host name or address>   # e.g., localhost, 127.0.0.1, or a public IP
PORT=<port number>              # default: 5432
NAME_DATABASE=<database name>   # e.g., my_db
NAME_USER=<role>                # e.g., Alice
PASSWORD_USER=<password>        # e.g., 123abc
```

You may place this file anywhere on the client machine. Importantly,
this step is optional. You can also provide the variables interactively
via terminal prompts.

### When to be used?

Use this approach if an SSH tunnel is not needed. This is the case if:

- the server and client run on the same machine,
- the server and client are in the same (virtual) network, or
- the server is accessible via its public IP.

### Connecting

In this case, simply run the Python script:

``` python
import pypsql
from pathlib import Path

sql_script = """
SELECT *
FROM customers
"""

# local connection
conn = pypsql.DatabaseConnector(
    db_credential_file='.env_local'
)

df = conn.get_data(sql_script)
print(df)
```

## Usage via an SSH Tunnel

### Provide database & SSH credentials

Again, create an `.env` file. You may want to store it in the same
directory as the Python script that accesses the database when executed.
This time the `.env` needs to follow this structure:

``` python
SERVER=<host name or address>              # e.g., localhost, 127.0.0.1
PORT=<port number>                         # default: 5432
NAME_DATABASE=<database name>              # e.g., my_db
NAME_USER=<role>                           # e.g., Alice
PASSWORD_USER=<password>                   # e.g., 123abc
SSH_USERNAME=<public IP of remote server>
SSH_PKEY=<path of private SSH key>         # e.g., ~/.ssh/id_rsa
SSH_PORT=<ssh port of remote server>       # default: 22
```

### Connecting

Then you can connect to the database via the SSH tunnel in the following
way:

``` python
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
```

# Official Documentation

The documentation is hosted under
<https://www.marius-liebald.com/pypsql/index.html>

# License

The package is distributed under the [MIT license](LICENSE.txt).

# References

<div id="refs" class="references csl-bib-body hanging-indent"
entry-spacing="0">

<div id="ref-sqlalchemy2025" class="csl-entry">

Bayer, Michael, and contributors. 2025. “SQLAlchemy.”
<https://www.sqlalchemy.org/>.

</div>

</div>
