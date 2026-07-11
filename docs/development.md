# Development

## Requirements

- Docker Engine 23 or newer
- Docker Compose v2
- Git
- Python 3.10 or newer for repository checks

Copy `.env.example` to `.env`, replace local passwords, then run the commands in
the main README. `.localhost` hostnames resolve to the local machine without a
hosts-file change in modern browsers.

Source development for `loopjet_frappe_custom` should use a Frappe Bench
development container. Production images are immutable and should not be edited
inside running containers.

Before committing:

```bash
./scripts/validate-config.py
./scripts/generate-apps.py --output /tmp/apps.json
python -m unittest discover -s tests
```
