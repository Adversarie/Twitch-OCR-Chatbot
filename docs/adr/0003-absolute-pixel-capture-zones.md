# Absolute Pixel Capture Zones Over Normalized Floats

Capture zone bounding boxes in `zones.json` are stored as absolute integer pixel dimensions and coordinates rather than normalized float percentages (0.0 to 1.0) of monitor resolution. Game user interfaces in Path of Exile and World of Warcraft exhibit non-linear scaling across resolution changes and ultrawide aspect ratios, making percentage-based coordinates inaccurate. Absolute pixels combined with an interactive visual ZoneEditor overlay provide exact, pixel-perfect alignment without complex scaling mathematics.
