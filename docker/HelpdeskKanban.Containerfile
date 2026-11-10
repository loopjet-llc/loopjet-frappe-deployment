ARG BASE_IMAGE=ghcr.io/loopjet-llc/loopjet-frappe-suite@sha256:488a11b1a8a13e1cf97edbe316b5aa58d86c75eaf91e3fefdff372ec073143ec
FROM ${BASE_IMAGE} AS helpdesk_builder
USER frappe
WORKDIR /home/frappe/frappe-bench/apps/helpdesk
COPY --chown=frappe:frappe helpdesk-kanban.patch /tmp/helpdesk-kanban.patch
RUN git apply --check /tmp/helpdesk-kanban.patch && git apply /tmp/helpdesk-kanban.patch
WORKDIR /home/frappe/frappe-bench/apps/helpdesk/desk
RUN printf '{"socketio_port":9000}\n' > /home/frappe/frappe-bench/sites/common_site_config.json \
    && yarn install --production=false --frozen-lockfile --non-interactive \
    && yarn build

FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.revision="abd86213c2255e378eb9c31b5c30ed424fd4cfb7"
COPY --from=helpdesk_builder --chown=frappe:frappe /home/frappe/frappe-bench/apps/helpdesk/desk/src/components/ticket/TicketKanban.vue /home/frappe/frappe-bench/apps/helpdesk/desk/src/components/ticket/TicketKanban.vue
COPY --from=helpdesk_builder --chown=frappe:frappe /home/frappe/frappe-bench/apps/helpdesk/helpdesk/api/doc.py /home/frappe/frappe-bench/apps/helpdesk/helpdesk/api/doc.py
COPY --from=helpdesk_builder --chown=frappe:frappe /home/frappe/frappe-bench/apps/helpdesk/helpdesk/public/desk/ /home/frappe/frappe-bench/apps/helpdesk/helpdesk/public/desk/
COPY --from=helpdesk_builder --chown=frappe:frappe /home/frappe/frappe-bench/apps/helpdesk/helpdesk/www/helpdesk/index.html /home/frappe/frappe-bench/apps/helpdesk/helpdesk/www/helpdesk/index.html
