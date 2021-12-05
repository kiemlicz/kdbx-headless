# KDBX headless
Simple server to expose KDBX entries via REST API

# Installation
Depends on desired type: either for development purposes or non-dev

## Non-development
1. create `docker-compose.override.yml` and set two volumes: `kdbx`, `kdbx-headless`.  
In `kdbx-headless` ensure `ssl` directory with CA, this kdbx-headless app certs (create them) and config  
In `kdbx` provide KDBX database
Example `docker-compose.override.yml`
```
volumes:
  kdbx-headless:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /home/theuser/bla/bla
  kdbx:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /home/theuser/bla/bla
```
3. `docker-compose up`

## Development
Run `bin/kh.py` (there is also IntelliJ run configuration available to run that for you)