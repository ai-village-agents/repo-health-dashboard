import sys
sys.path.insert(0, '.')
from src.scanner.pages_status import scan_pages

results = scan_pages()
live = [r for r, s in results.items() if s['live']]
print(f'Live: {len(live)}/{len(results)}')
print('Live repos:')
for r in live:
    print(f'  {r}')
print('\n404/Blocked repos:')
for r, s in results.items():
    if not s['live']:
        print(f'  {r}: HTTP {s.get("status_code", "unknown")}')
