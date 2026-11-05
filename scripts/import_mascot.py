"""Import unchanged official PNG bytes by approved SHA-256, not by ZIP filename."""
from pathlib import Path
import argparse, zipfile, hashlib, json
p=argparse.ArgumentParser();p.add_argument("zip_path");args=p.parse_args()
expected={"b546e162beb2bdffdc25b128cc900cf60e572cc41c5adf081b42dc4cb7570a63":"mascot-character-sheet-v0.1.png","9c694a3d5678751225be82cd69e5446a1b99a758682106333c79ae5b87cce06f":"mascot-pose-sheet-v0.1.png"}
found={}
with zipfile.ZipFile(args.zip_path) as z:
    for entry in z.infolist():
        if entry.is_dir() or entry.file_size>30_000_000:continue
        raw=z.read(entry)
        digest=hashlib.sha256(raw).hexdigest()
        if digest in expected:
            assert raw.startswith(b"\x89PNG\r\n\x1a\n"),"Not a PNG"
            found[digest]=raw
assert set(found)==set(expected),"Both approved original PNGs are required; nothing written"
target=Path(__file__).resolve().parents[1]/"assets/mascot/reference"
target.mkdir(parents=True,exist_ok=True)
for digest,raw in found.items():
    out=target/expected[digest]
    if out.exists():assert out.read_bytes()==raw,"Refusing to replace an existing master"
for digest,raw in found.items():
    out=target/expected[digest];out.write_bytes(raw)
    assert hashlib.sha256(out.read_bytes()).hexdigest()==digest
print(json.dumps({expected[d]:d for d in found},indent=2))
print("Original bytes verified. Commit, re-fetch GitHub blobs, and verify again before acceptance.")
