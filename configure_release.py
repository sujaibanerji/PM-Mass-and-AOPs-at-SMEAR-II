"""Change only archive URLs, retaining size/SHA-256 pins; never resolves a moving latest release."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url',required=True,help='Exact HTTPS release asset base, ending in the unique release tag.')
    a=p.parse_args()
    base=a.base_url.rstrip('/')
    if urlparse(base).scheme!='https' or '/latest' in base:
        p.error('Use an exact version-specific HTTPS base URL, never /latest.')
    file=Path(__file__).resolve().parent/'binder_release.json'
    config=json.loads(file.read_text(encoding='utf-8'))
    for r in config['archives'].values():
        r['url']=base+'/'+r['filename']
    file.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    print('URLs updated; archive hashes/sizes retained. Commit this configuration before pinning the launch URL.')

if __name__=='__main__':
    main()
