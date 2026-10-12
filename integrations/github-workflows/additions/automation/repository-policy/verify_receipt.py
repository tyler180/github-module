#!/usr/bin/env python3
"""Recheck an OFFLINE receipt binding; never authorizes deployment."""
import argparse
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location("policy", Path(__file__).with_name("policy.py"))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def verify(receipt, configuration, saved_plan, plan_json, policy_file, now, trusted_inputs, configuration_sha, policy_sha, base_sha):
    policy.require(receipt.get("schema_version") == 1 and receipt.get("result") == "pass" and receipt.get("mode") == "offline-fixture" and receipt.get("deployment_authorized") is False, "Unsupported or falsely authorized receipt")
    expected = {
        "configuration_digest": policy.tree_digest(configuration),
        "saved_plan_digest": policy.digest(Path(saved_plan).read_bytes()),
        "plan_json_digest": policy.digest(Path(plan_json).read_bytes()),
        "policy_implementation_digest": policy.digest(Path(policy_file).read_bytes()),
    }
    policy.require(all(receipt.get(key) == value for key, value in expected.items()), "Receipt binding mismatch")
    policy.require(receipt.get("configuration_sha") == configuration_sha and receipt.get("policy_sha") == policy_sha, "Receipt revision mismatch")
    policy.require(receipt.get("base_sha") == base_sha and trusted_inputs["record"].get("configuration_sha") == base_sha, "Accepted base revision changed")
    policy.require(receipt.get("input_digests") == {key: policy.digest(policy.canonical(value)) for key, value in trusted_inputs.items()}, "Trusted inputs changed since evaluation")
    age = now - policy.timestamp(receipt.get("evaluated_at", ""))
    policy.require(timedelta(0) <= age <= policy.FRESHNESS, "Expired policy receipt")
    policy.evaluate(trusted_inputs["base"], trusted_inputs["record"], trusted_inputs["candidate"], trusted_inputs["evidence"], trusted_inputs["plan-json"], now)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("receipt", "configuration", "saved-plan", "plan-json", "base", "base-sha", "record", "evidence", "configuration-sha", "policy-sha"):
        parser.add_argument("--" + arg, required=True)
    args = parser.parse_args()
    try:
        trusted_inputs = {key: policy.load_json(getattr(args, key.replace("-", "_"))) for key in ("base", "record", "evidence", "plan-json")}
        trusted_inputs["candidate"] = policy.load_json(Path(args.configuration) / "repositories.json")
        verify(policy.load_json(args.receipt), args.configuration, args.saved_plan, args.plan_json,
               Path(__file__).with_name("policy.py"), datetime.now(timezone.utc), trusted_inputs,
               args.configuration_sha, args.policy_sha, args.base_sha)
        print("Offline binding verified. Deployment remains unauthorized.")
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print("Receipt verification failed: " + (str(error) if isinstance(error, policy.PolicyError) else type(error).__name__), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
