#!/usr/bin/env python3
# builds both search indexes: small -> inline JSON in search/index.html (method A),
# big -> /home/sean/a/adata/local/site_corpus.jsonl for .post/search (method B).
# corpus = git-tracked files of public repos only (tracked == public by definition).
import json,re,subprocess,pathlib
SITE=pathlib.Path(__file__).resolve().parent
def tracked(repo,*paths):
    for f in subprocess.run(['git','-C',str(repo),'ls-files','--']+list(paths),
                            capture_output=True,text=True).stdout.split('\n'):
        if not f:continue
        p=pathlib.Path(repo,f)
        try:t=p.read_text(errors='replace')
        except (OSError,UnicodeError):continue
        if '��' in t[:4096] or len(t)>524288:continue  # binary-ish or huge
        yield f,t
small,big=[],[]
for f,t in tracked(SITE):
    if f.startswith('.post/')or f=='CNAME':continue
    u='/'+(f[:-10] if f.endswith('index.html') else f)
    small.append(['site/'+f,u,t]);big.append({'p':'site/'+f,'u':u,'t':t})
for f,t in tracked('/home/sean/a','IDEAS.md','README.md','AGENTS.md'):
    small.append(['a/'+f,'https://github.com/seanpattencode/a/blob/main/'+f,t])
for repo,pref in[('/home/sean/a','a'),('/home/sean/e','e')]:
    for f,t in tracked(repo):
        big.append({'p':pref+'/'+f,'u':f'https://github.com/seanpattencode/{pref}/blob/main/{f}','t':t})
js=json.dumps(small,ensure_ascii=False).replace('</','<\\/')
page=SITE/'search/index.html'
page.write_text(re.sub(r'(<script id=idx type=application/json>).*?(</script>)',
    lambda m:m.group(1)+js+m.group(2),page.read_text(),flags=re.S))
cor=pathlib.Path('/home/sean/a/adata/local/site_corpus.jsonl')
cor.write_text('\n'.join(json.dumps(d,ensure_ascii=False)for d in big))
print(f"inline: {len(small)} docs {len(js)>>10}KB -> {page}")
print(f"server: {len(big)} docs {cor.stat().st_size>>10}KB -> {cor}")
