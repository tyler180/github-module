mock_provider "github" {}
variables {
  owner          = "offline-fixture-owner"
  inventory_file = "tests/create.json"
}
run "no_early_developer_grants" {
  command = plan
  assert {
    condition     = toset(module.repositories["pilot"].managed_components.team_grants) == toset(["fixture-provisioner"])
    error_message = "Create stage must omit developer grants."
  }
}
run "grant_configuration" {
  command = plan
  variables { inventory_file = "tests/grant.json" }
  assert {
    condition     = length(module.repositories["pilot"].managed_components.team_grants) == 2
    error_message = "Grant stage includes both separately classified team sets."
  }
}
run "unknown_stage" {
  command = plan
  variables { inventory_file = "tests/invalid.json" }
  expect_failures = [terraform_data.contract]
}
