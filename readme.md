Personal Website. Accessible at [seanpatten.com](https://seanpatten.com/)

Goals: Minimize load speed, no cumulative layout shift, minimal and modern design asthetic. 

Features:  
Stripped down to be as performant as possible, with objective of fast loading times and smooth user experience.  
No use of images or any externally loaded resources.  
Use of native fonts. Although roboto is hinted, no external fonts are actually downloaded, preventing any cumulative layout shift and using native os fonts only.  
Single file that is 4.31 KB means fast loading on all connections.  
No seperate ICO for favicon, therefore no seperate request, instead computer emoji is used and described in html file.  


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
