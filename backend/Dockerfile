# Dockerfile — outline only, no implementation yet.
#
# Builds the backend into an image that runs uvicorn serving the FastAPI
# app. Single-stage is fine here (unlike the frontend) — there's no
# separate "build" step, Python just runs.
#
# Steps this needs, roughly in order:
#   1. FROM a Python base image (check: does it need to be ARM-
#      compatible / multi-arch, since the target VM is Oracle's Ampere
#      A1? per the blueprint's "worth knowing going in" note)
#   2. set a working directory
#   3. copy requirements.txt and install dependencies — BEFORE copying
#      the rest of the app code. This ordering matters for Docker's
#      layer caching: dependencies change less often than app code, so
#      putting them first means rebuilds are faster when you're only
#      editing .py files.
#   4. copy the rest of the app/ code in
#   5. EXPOSE the port uvicorn will listen on
#   6. CMD to actually run uvicorn
#
# Worth thinking about: secrets (DB password, JWT key) do NOT belong in
# this file as ENV lines — per the blueprint, those get injected at
# container runtime via env_file, not baked into the image.
