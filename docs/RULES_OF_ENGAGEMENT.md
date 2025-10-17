# Rules of Engagement for SRE Chaos Challenge Contributors

## Purpose
This document outlines the rules and expectations for all contributors participating in the SRE Chaos Challenge. Adhering to these rules ensures a fair, secure, and educational environment for everyone.

## Allowed Actions
Contributors are encouraged to:
- Deploy their own applications within their designated contributor directory.
- Implement advanced architectural patterns (e.g., load balancers, caching layers, auto-scaling solutions) to improve their application's resilience and performance.
- Interact with the `url-anvil` service as a target for their solutions.
- Utilize the provided metrics and registration endpoints of the backend API.
- Experiment with different strategies to optimize their scores within the challenge rules.

## Disallowed Actions
Contributors must NOT:
- Attempt to directly modify the `url-anvil` service or any core platform services.
- Attempt to bypass or interfere with the platform's scoring mechanisms.
- Engage in any activity that could disrupt the stability or availability of the platform for other users.
- Exceed resource limits (see Resource Usage below).
- Attempt to gain unauthorized access to any part of the platform.

## Resource Usage
All contributor applications are subject to resource limits to ensure fairness and prevent abuse. These limits will be enforced using Kubernetes `ResourceQuotas` and `LimitRanges` in cloud deployments. For more details, refer to the [Cloud Resource Management Strategy](./private/architecture/CLOUD_RESOURCE_MANAGEMENT.md) document.

## Interaction with `url-anvil` and Backend API
- Contributors should interact with `url-anvil` via its exposed HTTP endpoints.
- All metric submissions and challenge registrations must be done through the designated backend API endpoints using valid API keys.

## Fair Play Policy
- The spirit of the SRE Chaos Challenge is about learning and applying SRE principles. Any attempts to exploit loopholes or engage in unfair practices will result in disqualification.
- Collaboration on general SRE principles and strategies is encouraged, but direct sharing of challenge-solving code or specific exploits is prohibited.
