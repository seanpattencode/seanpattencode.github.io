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
1781256812
