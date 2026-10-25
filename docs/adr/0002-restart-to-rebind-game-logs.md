# Requiring Bot Restart to Re-bind Game Logs

When a user modifies the target game or log file paths in the GUI settings, OCR capture zones reload dynamically, but native log file watchers do not hot-reload open file handles. We decided to require the user to restart the bot via the GUI (Stop -> Start) to re-bind game log watchers rather than building dynamic task cancellation and file descriptor re-binding. This avoids concurrency race conditions, orphaned async file-tailing tasks, and leaky file descriptors for a configuration change that only occurs once per gaming session.
