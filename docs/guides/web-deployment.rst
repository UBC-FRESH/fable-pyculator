Web Deployment
==============

The portal is a local-first FastAPI service. It can run directly on a workstation, behind a
Jupyter/codeserver proxy, behind nginx/Caddy, or as a systemd service.

Local run
---------

.. code-block:: bash

   scripts/run_portal.sh

Defaults:

.. code-block:: text

   host:     127.0.0.1
   port:     8768
   runtime:  runtime/portal
   assistant: disabled

Direct CLI:

.. code-block:: bash

   .venv/bin/fable-pyculator web --root . --host 127.0.0.1 --port 8768

Authenticated remote access
---------------------------

A non-loopback bind requires explicit opt-in. Add built-in HTTP Basic auth or put the portal behind
an authenticating reverse proxy. Built-in auth is configured with two values:

.. code-block:: bash

   FABLE_PORTAL_HOST=0.0.0.0 \
   FABLE_PORTAL_ALLOW_REMOTE=1 \
   FABLE_PORTAL_AUTH_USER=operator \
   FABLE_PORTAL_AUTH_PASSWORD='a-long-random-password' \
   scripts/run_portal.sh

The unauthenticated exception is ``GET /api/health`` so a monitor can check liveness. Every API and
static asset otherwise requires Basic auth when configured.

Jupyter / codeserver proxy
--------------------------

If the portal is published under a path such as
``/user/me/proxy/8768``, pass the same prefix as ``--root-path``:

.. code-block:: bash

   FABLE_PORTAL_ROOT_PATH=/user/me/proxy/8768 \
   FABLE_PORTAL_HOST=0.0.0.0 \
   FABLE_PORTAL_ALLOW_REMOTE=1 \
   scripts/run_portal.sh

The SPA uses relative API/static URLs, so it works at ``/`` and under a prefix. Make sure the proxy
URL ends with a trailing slash; a bare path can resolve relative assets incorrectly. The example
nginx config redirects ``/fable`` to ``/fable/``.

Systemd
-------

Example files:

.. code-block:: text

   deploy/fable-pyculator-portal.service
   deploy/portal.env.example
   deploy/nginx-fable-portal.conf.example

Install outline:

.. code-block:: bash

   sudo install -d -o fable-portal -g fable-portal /opt/fable-pyculator /var/lib/fable-pyculator
   # install/extract the package and venv under /opt/fable-pyculator
   sudo install -m 600 deploy/portal.env.example /etc/fable-pyculator/portal.env
   sudo install -m 644 deploy/fable-pyculator-portal.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now fable-pyculator-portal

Edit the environment file before starting. In particular, set a real password, keep
``FABLE_PORTAL_ALLOW_AGENT=0`` unless the local assistant is intended, and point
``FABLE_PORTAL_ROOT``/``FABLE_PORTAL_RUNTIME`` at persistent paths.

Reverse proxy
-------------

The example nginx config terminates TLS and proxies to loopback. If the portal is mounted under
``/fable/``, use ``FABLE_PORTAL_ROOT_PATH=/fable``. Keep ``FABLE_PORTAL_HOST=127.0.0.1`` when nginx
is on the same host. Set a long ``proxy_read_timeout`` because generated-model runs and prepared
specs can take minutes.

Security boundaries
-------------------

- The portal has no user accounts or per-user isolation.
- Basic auth is a single shared credential; use a reverse proxy for stronger controls.
- The assistant is disabled by default. With ``FABLE_PORTAL_ALLOW_AGENT=1`` it runs the local
  ``opencode`` CLI with shell and repository access.
- Source workbooks, generated models, saved runs, chats, and caches are local files. Keep the
  runtime directory on a controlled filesystem.
- Do not expose the service directly to the public internet without TLS and authentication.

Public deployment handoff
-------------------------

A public deployment is a maintainer-controlled action. Before provisioning anything, collect these
inputs and record them in the deployment report:

- public hostname and DNS owner;
- TLS approach and certificate/ACME owner;
- reverse-proxy path, including whether the portal is mounted at ``/`` or a prefix such as ``/fable``;
- credential source for ``FABLE_PORTAL_AUTH_USER`` and ``FABLE_PORTAL_AUTH_PASSWORD``;
- service user, install root, runtime root, and backup location;
- whether the local assistant is enabled, and who owns the OpenCode process and its access;
- monitoring target for ``GET /api/health`` and the expected public/private boundary;
- firewall, proxy timeouts, and maximum upload/response settings;
- the named maintainer who will approve the deployment and receive the rollback instructions.

After those inputs exist, the deployment sequence is:

1. Build and pass the release-candidate checks.
2. Install the wheel and runtime under the agreed service paths.
3. Configure the environment file with a real password, then start the systemd unit or proxy wrapper.
4. Verify unauthenticated ``GET /api/health`` succeeds and every other route returns ``401``.
5. Verify the SPA, static assets, and one prepared model run through the public prefix.
6. Record the URL, commit, package version, workflow runs, and any limits in the phase report.
7. Keep the previous package artifact and runtime backup available for rollback.

No password, token, private workbook, or personal path belongs in a tracked file.
