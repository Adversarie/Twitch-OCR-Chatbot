Type: task
Status: resolved
Blocked by: 01

## Question

How do we implement the Visual Zone Editor in the browser? We need an endpoint (`/api/screenshot`) that uses `mss` to take a screenshot, and an HTML5 Canvas interface to draw boxes and save them back to `zones.json`.

## Answer

Created `GET /api/screenshot` endpoint in `web.py` using `mss` to capture the primary monitor and serve it as a PNG stream. Created `GET/POST /api/zones` to read and write `zones.json`. Added an HTML5 Canvas implementation in `index.html` where users can view existing bounding boxes, click and drag to draw new ones over the screenshot background, and save the updated coordinates.
