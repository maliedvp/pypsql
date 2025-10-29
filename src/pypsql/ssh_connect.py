# ssh_connect.py
import os
import pathlib
import paramiko
from sshtunnel import SSHTunnelForwarder
from .connect import DatabaseConnector, get_credentials

class SSHDatabaseConnector:
    """Establish a secure SSH tunnel to a remote database host and manage connections.

    This class creates an SSH tunnel to a remote database server, forwarding a local port to
    the remote host and port defined in a credentials file. It integrates with
    :class:`DatabaseConnector` to enable data operations (query, insert, drop, execute) over the
    secure tunnel.

    The SSH connection uses a specified private key and credentials defined in a `.env` file.
    Once connected, database queries can be executed transparently through the tunnel.

    Args:
        ssh_port (int, optional): SSH port on the remote host. Defaults to 22.
        ssh_key_passphrase (str | None, optional): Passphrase for the SSH private key if encrypted.
            Defaults to None.
        db_credential_file (str, optional): Name of the credentials file containing both SSH and
            database connection information. Defaults to ".env".
        path (pathlib.Path, optional): Path to the directory containing the credentials file.
            Defaults to the current working directory.

    Raises:
        ValueError: If the credentials file is missing required keys or if the port is invalid.
        RuntimeError: If the SSH tunnel fails to establish.
    """
    def __init__(
        self,
        ssh_port: int = 22,
        ssh_key_passphrase: str | None = None,
        db_credential_file: str = ".env",
        path: pathlib.Path = pathlib.Path.cwd(),
    ):
        self.path = path
        self.db_credential_file = db_credential_file

        # 1) Read remote DB endpoint from credentials (no manual host/port)
        # and information on the host
        credentials = get_credentials(self.path, self.db_credential_file)
        rb_host = credentials['SERVER']
        rb_port = credentials['PORT']
        self.server = credentials['SERVER']

        ssh_host = credentials['SSH_HOST']
        ssh_username = credentials['SSH_USERNAME']
        ssh_pkey = credentials['SSH_PKEY']
        ssh_port = int(credentials.get('SSH_PORT', ssh_port))

        if not rb_host or not rb_port:
            raise ValueError(
                "Missing SERVER and/or PORT in credentials file. "
                "Expected keys: SERVER, PORT, NAME_DATABASE, NAME_USER, PASSWORD_USER."
            )
        try:
            rb_port = int(rb_port)
        except (TypeError, ValueError) as e:
            raise ValueError(f"PORT must be an integer, got: {rb_port!r}") from e

        # Prevent Paramiko from probing other keys (like ~/.ssh/id_ed25519)
        os.environ.pop("SSH_AUTH_SOCK", None)

        # Load ONLY the specified private key
        pkey_path = str(pathlib.Path(ssh_pkey).expanduser())
        key = paramiko.Ed25519Key.from_private_key_file(
            pkey_path,
            password=ssh_key_passphrase  # None if unencrypted
        )

        # Start SSH tunnel: local listens on ephemeral port; remote is from creds
        self._tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_pkey=key,
            allow_agent=False,
            local_bind_address=("127.0.0.1", 0),        # ephemeral local port
            remote_bind_address=(rb_host, rb_port),     # from credentials file
            set_keepalive=30.0,
            mute_exceptions=False,
        )
        try:
            self._tunnel.start()
        except Exception as e:
            try:
                if getattr(self, "_tunnel", None) and self._tunnel.is_active:
                    self._tunnel.stop()
            except Exception:
                pass
            raise RuntimeError(
                f"Failed to establish SSH tunnel to {ssh_host}:{ssh_port} -> {(rb_host, rb_port)}"
            ) from e

        assigned_port = int(self._tunnel.local_bind_port)

        # Now create the DB connector: user/pass/db still come from the same creds
        self.db = DatabaseConnector(path=self.path, db_credential_file=self.db_credential_file)

        self.db.server = "127.0.0.1"
        self.db.port = str(assigned_port)
        self.db.engine = self.db._reconnect_engine()

    # Delegations
    def get_data(self, *args, **kwargs): 
        return self.db.get_data(*args, **kwargs)

    def push_data(self, *args, **kwargs): 
        return self.db.push_data(*args, **kwargs)

    def drop_table(self, *args, **kwargs): 
        return self.db.drop_table(*args, **kwargs)

    def execute_script(self, *args, **kwargs): 
        return self.db.execute_script(*args, **kwargs)

    # Cleanup / context manager
    def close(self):
        try:
            if hasattr(self, "_tunnel") and self._tunnel.is_active:
                self._tunnel.stop()
        except Exception:
            pass

    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): self.close(); return False
    def __del__(self): self.close()