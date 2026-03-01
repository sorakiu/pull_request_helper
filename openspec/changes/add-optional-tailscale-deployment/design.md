## Context
The Pull Request Helper project is a portfolio application with planned frontend and backend components. Deployment currently lacks private access options. Stakeholders include developers who want to demo or test the application privately without public exposure.

## Goals / Non-Goals
- Goals: Provide optional Tailscale connectivity for private access during deployment
- Non-Goals: Make Tailscale mandatory, replace all networking, support other VPN solutions

## Decisions
- Decision: Use Tailscale auth key for authentication in deployment scripts
- Alternatives considered: Tailscale OAuth (more complex for automated deployment), manual setup (not automated)

## Risks / Trade-offs
- Security risk of auth key exposure → Mitigation: Store as secret, rotate regularly
- Deployment complexity increase → Mitigation: Make it optional, well-documented

## Migration Plan
No migration needed as this is an optional new feature. Existing deployments continue unchanged.

## Open Questions
- How to handle Tailscale IP assignment for multiple deployments?
answer: not a worry - you should only ever deploy this once per ts network
- Should we support Tailscale tags for access control?
answer: no
