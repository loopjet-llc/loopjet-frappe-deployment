# Invoice-only release: preserve the exact running platform and its dependencies.
FROM ghcr.io/loopjet-llc/loopjet-frappe-suite@sha256:419de209aa9ebd35b47c394f570e482b95211b5faa95952a8cb967117d519a42
USER root
COPY --chown=frappe:frappe .invoice-custom/loopjet_frappe_custom/ /home/frappe/frappe-bench/apps/loopjet_frappe_custom/loopjet_frappe_custom/
USER frappe
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir --no-deps --editable /home/frappe/frappe-bench/apps/loopjet_frappe_custom
