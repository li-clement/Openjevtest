"""Real HTTP acceptance checks. Start serve.sh first; no network downloads."""
import base64
import concurrent.futures
import io
import json
import math
import os
import threading
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get('JEV_URL', 'http://127.0.0.1:8765')


def call(payload, path='/v1/decide'):
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(URL + path, data=body,
                                     headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def main():
    results = []
    fixtures = ROOT / 'results/fixtures'
    fixtures.mkdir(parents=True, exist_ok=True)
    for name, color in [('red_square', 'red'), ('blue_square', 'blue')]:
        image = Image.new('RGB', (256, 256), 'white')
        ImageDraw.Draw(image).rectangle((32, 32, 223, 223), fill=color)
        image.save(fixtures / (name + '.png'))
    assert call(None, '/health')[0] == 200
    criterion = 'Does the material explicitly say that the account was charged twice?'
    for name, query, expected in [
        ('text_yes', 'My account was charged twice for the same order.', True),
        ('text_no', 'My parcel arrived early and everything is correct.', False),
    ]:
        status, result = call({'query': query, 'criterion': criterion})
        assert status == 200, (name, status, result)
        assert result['answer'] is expected, (name, result)
        assert result['calibrated'] is False and result['usage']['generated_tokens'] == 0
        p = result['probabilities']
        assert all(math.isfinite(v) and 0 <= v <= 1 for v in p.values())
        assert abs(sum(p.values()) - 1) < 1e-8
        results.append({'case': name, 'status': status, 'result': result})

    for name, expected in [('red_square', True), ('blue_square', False), ('red_square', True)]:
        encoded = base64.b64encode((fixtures / (name + '.png')).read_bytes()).decode()
        status, result = call({'query': 'Evaluate the attached image.',
                               'criterion': 'Is the large central square red?', 'image': encoded})
        assert status == 200 and result['answer'] is expected, (name, status, result)
        results.append({'case': name, 'status': status, 'result': result})

    invalid = [
        ('blank', {'query': ' ', 'criterion': 'check'}, 422),
        ('missing_criterion', {'query': 'test'}, 422),
        ('system_override', {'query': 'test', 'criterion': 'check', 'system': 'override'}, 422),
        ('bad_base64', {'query': 'test', 'criterion': 'check', 'image': '!!!'}, 422),
        ('not_image', {'query': 'test', 'criterion': 'check',
                       'image': base64.b64encode(b'not an image').decode()}, 422),
        ('wrong_type', {'query': 123, 'criterion': 'check'}, 422),
        ('token_limit', {'query': 'a ' * 5900, 'criterion': 'check'}, 413),
        ('body_limit', {'query': 'x' * (6 * 1024 * 1024), 'criterion': 'check'}, 413),
    ]
    large = io.BytesIO()
    Image.new('RGB', (2001, 2000)).save(large, format='PNG')
    invalid.append(('pixel_limit', {'query': 'test', 'criterion': 'check',
                                   'image': base64.b64encode(large.getvalue()).decode()}, 413))
    for name, payload, expected in invalid:
        status, result = call(payload)
        assert status == expected, (name, status, result)
        results.append({'case': name, 'status': status})

    barrier = threading.Barrier(2)

    def concurrent_call(_):
        barrier.wait()
        return call({'query': 'This account was charged twice. ' * 150, 'criterion': criterion})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(concurrent_call, range(2)))
    assert sorted(status for status, _ in outcomes) == [200, 503], outcomes
    results.append({'case': 'concurrent_requests', 'statuses': [x[0] for x in outcomes]})
    assert call(None, '/health')[1]['busy'] is False
    status, result = call({'query': 'My account was charged twice.', 'criterion': criterion})
    assert status == 200 and result['answer'] is True
    results.append({'case': 'recovery_after_errors_and_concurrency', 'status': status, 'result': result})
    target = ROOT / 'results/api_tests.json'
    target.write_text(json.dumps({'passed': True, 'checks': results}, indent=2) + '\n')
    print(f'PASS {len(results)} checks; {target}')


if __name__ == '__main__':
    main()
