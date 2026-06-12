#!/bin/sh
# Build ot.wasm and inline it (base64) into index.html. Requires clang + lld.
cd "$(dirname "$0")"
clang --target=wasm32 -O2 -nostdlib -Wl,--no-entry -Wl,--export=ot_boot \
    -Wl,--export=ot_feed -Wl,--export=ot_in -Wl,--export=ot_over -o ot.wasm ot.c || exit 1
python3 - <<'EOF'
import base64, re
b = base64.b64encode(open('ot.wasm', 'rb').read()).decode()
h = open('index.html').read()
h = re.sub(r"const B64='[^']*'", f"const B64='{b}'", h)
open('index.html', 'w').write(h)
print(f"inlined {len(b)} base64 bytes into index.html")
EOF
