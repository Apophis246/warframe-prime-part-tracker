# Dockerfile — outline only, no implementation yet.
#
# Multi-stage, per the blueprint: build the React app in one stage, then
# serve the static output with nginx in a second, smaller stage. The
# first stage's tooling (node_modules, source files) never ends up in
# the final image — only the built static files do.
#
# Stage 1 — build:
#   1. FROM a node base image
#   2. copy package.json (and lockfile) in, install dependencies
#   3. copy the rest of the frontend source in
#   4. run the production build command — produces a static output
#      folder (dist/ or build/, depending on your tooling)
#
# Stage 2 — serve:
#   1. FROM an nginx base image
#   2. copy the built static files from stage 1 into nginx's serve
#      directory (look up: Docker's multi-stage COPY --from=)
#   3. copy in a custom nginx.conf (not written yet — needed for
#      client-side routing to work on refresh, since React Router
#      handles routes in the browser, not on the server)
#   4. EXPOSE 80
#
# Worth checking: ARM compatibility again here too, same as the backend
# — confirm the node and nginx base images you pick have ARM builds.
