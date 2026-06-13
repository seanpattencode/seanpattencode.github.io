Personal Website focused on speed and performance. Accessible at [seanpatten.com](https://seanpatten.com/)

Goals: Minimize load time, no cumulative layout shift, minimal and modern design asthetic.

Features:
Stripped down to be as performant as possible, with objective of fast loading times and smooth user experience.
- No images or externally loaded resources.
- Native system fonts only. No layout shift, no extra requests.
- Single file, ~3 KB.
- No favicon request.

Tag set: strict subset of Tim Berners-Lee's original 1991 HTML — `<title>`, `<h1>`–`<h3>`, `<p>`, `<a>`, `<ul>`, `<li>`, `<hr>`, `<i>`, `<b>`. No `<div>`, `<section>`, `<header>`, `<article>` — none of those existed in 1991 and they aren't needed. Plus `<meta charset>` + `<meta viewport>` + a 11-line `<style>` block for modern typography (system-ui font, max-width, dark-mode aware via `color-scheme: light dark`). The semantic content renders correctly in every browser ever shipped, including 1993 Mosaic and text-only browsers like Lynx — the CSS is the only thing newer than 2009.


Performance Measured:  
As of 9/4/24 desktop results on [pagespeed.web.dev](https://pagespeed.web.dev/) are:  
First Contentful Paint  
0.2 s  
Largest Contentful Paint  
0.2 s  
Total Blocking Time  
0 ms  
Cumulative Layout Shift  
0  
Speed Index  
0.2 s  
With a score of 100 out of 100 on performance.  
These numbers have not changed as of 11/18/25.

It should also be noted 
- Human reaction time on average is about 200ms, 0.2 seconds, and therefore this should be at the threshold where humans would perceive loading as instant. 
- According to pagespeed google.com on desktop loads in 0.6 s

[/search/](https://seanpatten.com/search/) — search engine over the top 100,000 websites:
- Page is 2.8 KB (1.6 KB gzipped) — same weight class as this site. First paint ≤200 ms.
- The 100k-domain index (`domains.txt`, 630 KB gzip) streams *after* first paint, in rank order — google.com is in the first chunk, so the box is usable before the stream finishes. Full stream + index build: ~200 ms.
- Prefix tables (all completions to 3 chars) built incrementally as the stream arrives. No server, no request per keystroke.
- Measured per keystroke: 0–600 µs — results render before the next keystroke can physically arrive.
- Address bar: add `https://seanpatten.com/search/?q=%s` as a custom search engine; trailing `!` jumps to top hit.
1781256812
