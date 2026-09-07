# Customer-reports release: preserve the exact running platform and invoice release.
FROM ghcr.io/loopjet-llc/loopjet-frappe-suite@sha256:050d89a77adc4df3273dbd051687a063e03766178810b9e1bbe3335c12deb40f
USER root
COPY --chown=frappe:frappe .customer-reports-custom/loopjet_frappe_custom/ /home/frappe/frappe-bench/apps/loopjet_frappe_custom/loopjet_frappe_custom/
USER frappe
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir --no-deps --editable /home/frappe/frappe-bench/apps/loopjet_frappe_custom
