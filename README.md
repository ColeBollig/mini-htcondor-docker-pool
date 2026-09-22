# Miniature Dockerized HTCondor System

A small, self-contained [HTCondor](https://htcondor.org/) system built with Docker Compose — useful for demos, testing, and learning how an HTCondor system fits together, without needing real hardware.

## Architecture

```mermaid
flowchart LR
    subgraph compute["docker network: compute"]
        CM["Central Manager (CM)<br/>collector + negotiator"]
        AP["Access Point (AP)<br/>schedd"]
        EP["Execution Point (EP)<br/>startd"]
        Remote["Remote Submit Host (Remote)<br/>python bindings only"]
    end

    AP -- advertise schedd --> CM
    EP -- advertise startd --> CM
    CM -- match --> AP
    CM -- match --> EP
    AP <-- job execution --> EP
    Remote -- SSH: fetch IDTOKEN --> AP
    Remote -- submit jobs --> AP
```

- Central Manager: Host machine in charge of matching jobs to resources
- Access Point: Host machine that manages/tracks user jobs
- Execution Point: Host machine that executes user jobs
- Remote: Host machine with only python API installed for remote AP job placement

> [!NOTE]
> This miniature system is set up to use IDTOKEN authentication
> for everything.

## Docker Configuration

Controls docker build aspects defined in `.env`.

| Option | Purpose |
|---|---|
| CM_HOST | Central Manager hostname |
| AP_HOST | Access Point hostname |
| EP_HOST | Execution Point hostname |
| REMOTE_HOST | Remote submission hostname |
| SECRET | Shared secret for daemon idtoken signing |
| USER_PASSWORD | User password for ssh access |
| USER_NAME | Username for ssh access and job submission |

Edit these before building if you want different hostnames, credentials, or the shared signing secret.

## HTCondor Configuration

Custom HTCondor configuration can be specified before building the docker
containers in the following two methods:

1. Add configuration file to `system/config/` to control HTCondor behavior
   on the AP, EP, and CM.
2. Update `remote/user.conf` to control behavior on the remote submission
   host.

## Usage

The `htc` script wraps Docker Compose:

```
./htc fly       # build and start the system
./htc perch     # stop the system
./htc destroy   # stop the system and remove its images, volumes, and networks
./htc help      # usage
```

On startup it prints SSH login commands and the system user's password for each host.

## Logging in

```
ssh -p 2000 tweety@localhost   # Central Manager
ssh -p 2001 tweety@localhost   # Access Point
ssh -p 2002 tweety@localhost   # Execution Point
ssh -p 2003 tweety@localhost   # Remote submit host
```

## Submitting jobs

From `ap` (or `remote`), submit jobs as usual with `condor_submit`:

```
ssh -p 2001 tweety@localhost
condor_submit /path/to/job.sub
condor_q
```

`remote` has no local schedd — it submits through `ap` using the IDTOKEN it fetches at boot (see the Architecture note above).

## Troubleshooting

- **`remote` container logs repeat "Waiting for Access Point accessible via SSH"**: `ap` hasn't finished starting yet (or failed to start) — `remote` blocks on `condor_ping` over SSH to `ap` until it succeeds. Check `docker compose logs ap`.
- **Login fails / SSH connection refused**: give containers a few seconds after `./htc fly` for `sshd` and the HTCondor daemons to come up.
- **Rebuilding after changing `.env`**: `./htc perch` then `./htc fly` — hostnames and secrets are baked in at image build time via Dockerfile `ARG`s, so a plain restart won't pick up changes.

## Not for production

This is a demo/dev tool: passwords are stored in plaintext in `.env`, SSH allows password auth and root login, and the signing secret ships in the repo's default `.env`. Don't reuse these images or configs outside a local/throwaway environment.
