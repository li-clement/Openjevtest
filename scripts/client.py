"""Small standard-library HTTP client for the local decision API."""
import argparse
import base64
import json
from pathlib import Path
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--query', required=True)
parser.add_argument('--criterion', required=True)
parser.add_argument('--image', type=Path)
parser.add_argument('--url', default='http://127.0.0.1:8765')
args = parser.parse_args()
payload = {'query': args.query, 'criterion': args.criterion}
if args.image:
    payload['image'] = base64.b64encode(args.image.read_bytes()).decode()
request = urllib.request.Request(args.url.rstrip('/') + '/v1/decide',
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(request, timeout=90) as response:
        print(json.dumps(json.load(response), ensure_ascii=False, indent=2))
except urllib.error.HTTPError as error:
    print(error.read().decode())
    raise SystemExit(1)
