import os
import shutil
import subprocess
import json
import lzma as xz
import httpx

from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


from google.cloud import storage
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def download(url: str, filepath: str):
    """Downloads a file from a url."""
    print(f"Downloading {url} to {filepath}...")
    zipfile = url.endswith(".zip")
    if zipfile:
        print("Extracting zip file...")
        r = httpx.get(url, allow_redirects=True)
        with TemporaryDirectory() as tmpdir:
            zippath = Path(tmpdir) / "data.zip"
            with open(zippath, "wb") as f:
                f.write(r.content)
            with ZipFile(zippath, "r") as zip_ref:
                zip_ref.extractall(f"{tmpdir}/data")
                file = os.listdir(f"{tmpdir}/data")[0]
                shutil.move(f"{tmpdir}/data/{file}", filepath)
        return filepath
    url = url.replace("https", "http")
    try:
        subprocess.run(["wget", url, "-O", filepath])
        return filepath
    except Exception as e:
        print("wget failed:", e)
    r = httpx.get(url, allow_redirects=True)
    with open(filepath, "wb") as f:
        f.write(r.content)
    return filepath

def upload(from_path: Path, to_path: str):
    """Uploads a file to the bucket."""
    client = storage.Client()
    bucket = client.bucket(os.environ["BUCKET"])
    blob = bucket.blob(to_path)
    blob.upload_from_filename(from_path)
    return "gs://" + os.environ["BUCKET"] + "/" + to_path

def save_jsonl(jsonl_data, path, mode="w"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    openf = xz.open if path.suffix == ".xz" else open
    encodef = lambda x: x.encode("utf-8") if path.suffix == ".xz" else x
    with openf(path, mode) as f:
        for line in jsonl_data:
            f.write(encodef(json.dumps(line) + "\n"))

def read_jsonl(path):
    path = Path(path)
    openf = open if path.suffix != ".xz" else xz.open
    with openf(path, "r") as f:
        for line in f:
            yield json.loads(line)

def safe_remove_file(path):
    if os.path.exists(path):
        os.remove(path)