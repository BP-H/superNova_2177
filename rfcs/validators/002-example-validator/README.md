# Daily Participation Validator

<!-- Example path: rfcs/validators/002-example-validator/README.md -->

## Summary
This RFC introduces a lightweight rule for tracking daily participation. The validator records whether each participant performs at least one action per calendar day.

## Motivation
Consistent engagement keeps the network healthy. By logging minimal daily activity we can detect dormant accounts and encourage ongoing contribution.

## Specification
- Each day, the validator checks for any interaction from each participant (posts, votes, or logins).
- Absence of activity for more than `N` days triggers a soft alert to reengage the user.
- The rule can be implemented as a scheduled task querying activity logs.

## Rationale
Tracking daily participation is simple to implement yet provides insight into community health. It also creates opportunities to notify users before they fall completely inactive.

## Drawbacks
- May generate noise for users who intentionally take short breaks.
- Requires reliable activity logging infrastructure.

## Adoption Strategy
Deploy the validator in observation mode first, only sending notifications. After testing, it can enforce minimum activity with configurable grace periods.

## Unresolved Questions
- What default threshold of inactivity should trigger an alert?
- How can users opt out of reminders if desired?
