# WhyUser logo + favicon swap (happy judge)

Copy everything in this folder to your site root. Keep the folders.

New files
- favicon.ico                      16/32/48 px, face crop, for browser tabs
- apple-touch-icon.png             180 px, full head on white, for iPhone home screen
- images/whyuser-logo.png          512 px, real transparent PNG, header/footer/schema
- images/whyuser-favicon-192.png   192 px, for Google results and Android

Changed files
- 28 *.html   favicon links, logo paths, schema logo URL
- assets/whyuser-readability.css   logo swap rule now points to whyuser-logo.png

Safe to delete after deploy: images/whyuser-mark.png, images/whyuser-mark-dark.png,
images/whyuser-favicon.png, images/apple-touch-icon.png.

Browsers cache favicons hard. Links use ?v=2. Still stale? Hard-refresh or open a private window.
