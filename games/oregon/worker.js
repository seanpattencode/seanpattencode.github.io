/* Runs the unmodified oregon_trail.py in Pyodide. input() blocks this worker
   on a SharedArrayBuffer until the page sends a line — so the hunting timer
   measures real typing speed, like 1978. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.4/full/pyodide.js')
const out = new TextDecoder(), inp = new TextDecoder()
onmessage = async e => {
    const ctl = new Int32Array(e.data, 0, 2), buf = new Uint8Array(e.data, 8)
    try {
        const py = await loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/'})
        py.setStdout({write: b => (postMessage(out.decode(b, {stream: true})), b.length), isatty: true})
        py.setStderr({write: b => (postMessage(out.decode(b)), b.length)})
        py.setStdin({isatty: true, stdin: () => {
            Atomics.store(ctl, 0, 0); postMessage(0); Atomics.wait(ctl, 0, 0)
            return inp.decode(buf.slice(0, ctl[1])) + '\n'
        }})
        py.runPython('import sys;sys.argv=["oregon_trail.py"]')
        py.runPython(await (await fetch('oregon_trail.py')).text())
    } catch (err) {
        const m = String(err && err.message || err)
        if (!/SystemExit/.test(m)) postMessage('\n[ ' + m.trim().split('\n').pop() + ' ]')
    }
    postMessage('\n[ GAME OVER — refresh to ride again ]')
}
