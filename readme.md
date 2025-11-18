Personal Website focused on speed and performance. Accessible at [seanpatten.com](https://seanpatten.com/)

Goals: Minimize load time, no cumulative layout shift, minimal and modern design asthetic. 

Features:  
Stripped down to be as performant as possible, with objective of fast loading times and smooth user experience.  
- No use of images or any externally loaded resources.  
- Use of native fonts. Prevents any cumulative layout shift, loads faster, and reduces total data sent.  
- Single file that is 4.31 KB, leading to fast loading on all connections.  
- No seperate ICO for favicon, therefore no seperate request, instead computer emoji is used and described in html file.  


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
