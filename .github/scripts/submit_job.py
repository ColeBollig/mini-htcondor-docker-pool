#!/usr/bin/env python3
"""Submit a job directly to the AP's schedd and optionally wait for it to finish.

`remote` has no local schedd (and no condor_submit CLI - only the htcondor2
Python bindings are installed), so a job placed here has to locate the AP's
schedd through the CM's collector and submit to it directly. Authentication
uses the IDTOKEN fetched from AP at boot (see remote/boot.sh), which lives in
the default ~/.condor/tokens.d location the bindings already look at.
"""
import argparse
import os
import sys
import time

import htcondor2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", default=os.environ.get("CM_HOSTNAME"),
                         help="Central Manager hostname (collector)")
    parser.add_argument("--schedd", default=os.environ.get("AP_HOSTNAME"),
                         help="Access Point hostname (schedd)")
    parser.add_argument("--wait", action="store_true",
                         help="Wait for the job to finish and check its exit code")
    parser.add_argument("--timeout", type=int, default=120,
                         help="Seconds to wait for job completion with --wait")
    args = parser.parse_args()

    if not args.collector or not args.schedd:
        parser.error("--collector/--schedd (or CM_HOSTNAME/AP_HOSTNAME) are required")

    schedd_ad = htcondor2.Collector(args.collector).locate(
        htcondor2.DaemonType.Schedd, args.schedd
    )
    schedd = htcondor2.Schedd(schedd_ad)

    submit = htcondor2.Submit({
        "executable": "/bin/echo",
        "arguments": "hello from the remote submit host",
        "output": "remote-job.out",
        "error": "remote-job.err",
        "log": "remote-job.log",
        "initialdir": "/tmp",
        "should_transfer_files": "YES",
        "when_to_transfer_output": "ON_EXIT",
    })

    result = schedd.submit(submit)
    cluster_id = result.cluster()
    print(f"Submitted cluster {cluster_id} to {args.schedd} via {args.collector}")

    # Unlike the condor_submit CLI, Schedd.submit() doesn't nudge the
    # negotiator on its own - without this the job just waits for the next
    # periodic negotiation cycle (default ~60s), which can outrun --timeout.
    schedd.reschedule()

    if not args.wait:
        return

    # Poll condor_history rather than the live queue: a job only shows up
    # there once it has reached a genuinely terminal state, so there's no
    # "briefly empty" race to handle like there is with Schedd.query().
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        history = list(schedd.history(
            constraint=f"ClusterId == {cluster_id}",
            projection=["ExitCode"],
            match=1,
        ))
        if history:
            exit_code = history[0].get("ExitCode")
            print(f"Job {cluster_id} completed with exit code {exit_code}")
            sys.exit(0 if exit_code == 0 else 1)
        time.sleep(2)

    print(f"Timed out waiting for job {cluster_id} to complete", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
