# Raw-download correction: preserve the exact current customer-reports production image.
FROM ghcr.io/loopjet-llc/loopjet-frappe-suite@sha256:3a352ae8493323afa2d71a2252ab5693d52a17b7f635679697752c60cafa0454
USER root
COPY --chown=frappe:frappe .customer-reports-custom/loopjet_frappe_custom/ /home/frappe/frappe-bench/apps/loopjet_frappe_custom/loopjet_frappe_custom/
USER frappe
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir --no-deps --editable /home/frappe/frappe-bench/apps/loopjet_frappe_custom
