---
type: wayfinder:task
status: closed
assignee: agent
---

## Question

How should the visual scanner be implemented with OpenCV (`cv2.matchTemplate`) to scan full-screen captures in under 15ms against a bank of game reference templates, returning detected event IDs and bounding confidence without any user-configured zones?

## Resolution

Implemented `TemplateScanner` (`template_scanner.py`) utilizing OpenCV's normalized cross-correlation template matching (`cv2.matchTemplate` with `cv2.TM_CCOEFF_NORMED`):
- Scans entire screen captures against in-memory grayscale template assets in ~5-15ms without user bounding boxes.
- Evaluates against configurable confidence threshold (default 0.82), returning matching event IDs, locations, and confidence levels.
- Integrated into `OCRScanner` so full-screen template matching runs as the primary visual detection pass while preserving backward compatibility for remaining zones.
- Benchmarked and verified with synthetic detection test.
