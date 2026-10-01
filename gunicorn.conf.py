# Gunicorn settings for Railway.
# Gunicorn loads this file automatically when it sits in the folder you start from,
# so the start command can stay simply: gunicorn app:app

import os

# Railway tells the app which port to listen on through the PORT variable
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")

# One worker keeps memory low: every worker loads its own copy of the vector index,
# so 2 workers roughly doubles RAM (and the Railway bill).
# Threads let that single worker handle a few questions at the same time.
workers = 1
threads = 4

# LLM calls can take 10 to 30 seconds. Gunicorn's default 30s timeout
# would kill slow answers mid-response, so give it more room.
timeout = 120

# Send logs to stdout/stderr so they show up in Railway's log viewer
accesslog = "-"
errorlog = "-"
