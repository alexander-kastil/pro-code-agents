import mimetypes
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings

def get_blob_service_client() -> Optional[BlobServiceClient]:
    conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)

    account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    if account_name and account_key:
        account_url = f"https://{account_name}.blob.core.windows.net"
        return BlobServiceClient(account_url=account_url, credential=account_key)

    return None


def upload_folder(container_name: str, assets_dir: Path) -> None:
    client = get_blob_service_client()
    container_client = client.get_container_client(container_name)

    files = sorted(p for p in assets_dir.iterdir() if p.is_file())
    if not files:
        return

    for path in files:
        blob_name = path.name
        content_type, _ = mimetypes.guess_type(str(path))
        content_settings = ContentSettings(content_type=content_type) if content_type else None

        with path.open("rb") as f:
            data = f.read()

        container_client.upload_blob(
            name=blob_name, data=data, overwrite=True, content_settings=content_settings
        )


def main() -> None:
    load_dotenv()
    assets_dir = Path(os.environ["ASSETS_DIR"])
    container_name = os.environ["STORAGE_CONTAINER_NAME"]
    upload_folder(container_name=container_name, assets_dir=assets_dir)


if __name__ == "__main__":
    main()
