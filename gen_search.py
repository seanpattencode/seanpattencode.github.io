#!/usr/bin/env python3
# search index = top 100k real websites (Majestic Million), injected into search/index.html.
import json,pathlib,re,subprocess
N=100000
SITE=pathlib.Path(__file__).resolve().parent
cache=pathlib.Path('/home/sean/a/adata/local/top_domains.txt')
if not cache.exists() or len(cache.read_text().split())<N:
    csv=subprocess.run(f"curl -s https://downloads.majestic.com/majestic_million.csv|head -{N+1}",
        shell=True,capture_output=True,text=True).stdout
    doms=[l.split(',')[2].lower() for l in csv.splitlines()[1:] if l.count(',')>2]
    assert len(doms)>N*0.9,'download failed'
    cache.write_text('\n'.join(doms))
doms=cache.read_text().split()[:N]
js=json.dumps(doms,separators=(',',':')).replace('</','<\\/')
page=SITE/'search/index.html'
page.write_text(re.sub(r'(<script id=idx type=application/json>).*?(</script>)',
    lambda m:m.group(1)+js+m.group(2),page.read_text(),flags=re.S))
print(f"{len(doms)} domains {len(js)>>10}KB -> {page}")
