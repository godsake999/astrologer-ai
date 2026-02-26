
import httpx
from ai_engine import _load_keys
keys = _load_keys()
payload = {
    'model': keys['model'],
    'messages': [
        {'role': 'system', 'content': 'You are an astrologer.'},
        {'role': 'user', 'content': 'Test'}
    ],
    'temperature': 0.85,
    'max_tokens': 400
}
headers = {'Authorization': 'Bearer ' + keys.get('openrouter', '')}
try:
    r = httpx.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload, timeout=10)
    print('STATUS:', r.status_code)
    print('RESPONSE:', r.text)
except Exception as e:
    print('REQ FAILED:', e)

