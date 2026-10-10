# OLI RouteSave

**Save money. Travel smarter.**

OLI RouteSave is an Android-first travel and driver-assistance project. The current debug APK is an early test build; features listed below are planned unless explicitly verified in the app.

## Development priorities

### 1. Working route planning (first priority)
- Replace the placeholder route screen with a real map and a routing service.
- Resolve start and destination to actual places and allow the user to choose the correct result.
- Calculate road distance and estimated travel time from route data; never show invented/default kilometres.
- Calculate fuel cost from the saved vehicle's fuel consumption and the user's fuel price.
- Show data gaps clearly and do not imply that a route is verified when it is not.

### 2. Truck profile and truck-aware route checks
Allow a driver to save vehicle/suit dimensions and restrictions:
- vehicle combination/type;
- height, width, total length and gross weight;
- axle weights where needed;
- ADR transport details when applicable.

Routing should use a provider that explicitly supports the relevant truck restrictions. A generic car route must not be presented as a verified truck-safe route. Where reliable data is missing, warn the driver and offer a better-supported alternative if available.

### 3. Bridges, tunnels and ADR
- Highlight bridges and tunnels on the map when data is available.
- Show verified height, width, weight and other restrictions.
- For ADR journeys, check tunnel category and the actual transport/tunnel restriction code against current rules.
- Clearly distinguish prohibited, permitted and unknown/unverified passages.
- Do not infer safe passage from the absence of a mapped restriction.

### 4. Correct delivery entrance and final approach
Distinguish between:
- registered company/head-office address;
- operating site or warehouse;
- truck entrance/loading gate.

Add a “Truck Arrival Assist” mode for the final approach, with overhead and 3D views when supported, available imagery, entrance instructions and warnings about narrow roads, tight turns, dead ends and uncertain turning space. Never guarantee a turn-around or passage unless the required data supports that conclusion.

### 5. Community assistance and driver connections
Planned opt-in features:
- drivers' private messages and community notices;
- nearby-driver discovery and invitations to take a break together;
- requests for help finding a warehouse entrance or reporting a road issue;
- community-submitted entrance and road information with timestamps, verification status and reporting/moderation;
- local alerts and important route-related alerts for drivers approaching an affected area.

Location sharing must be voluntary, visible to the user, revocable and limited to the chosen purpose/time. Ask for clear confirmation before sending messages, requests or location. Include blocking and abuse-reporting controls.

### 6. Voice and map views
- Let the user choose an assistant and invoke it by its configured short name.
- Support overhead 2D and 3D navigation views, with voice commands to switch views.
- Keep driving interactions hands-free where technically possible and safe.
- External actions (calls, SMS, messages, requests and location sharing) require explicit confirmation.

### 7. Europe-first language and platform plan
Prioritize European coverage and the previously agreed European languages. Plan Android Auto support first, then compatible Android Automotive OS vehicles and Apple CarPlay subject to platform rules and technical feasibility. A companion website should eventually share accounts and community features with the mobile app.

## Current known test-build limitations
- The map/GPS screen is currently a placeholder, not a working live map.
- Route distance and travel time are not yet provided by a real routing engine.
- The route cost form must not prefill a fictitious distance.
- Voice recognition, assistant responses and community actions still need real-device testing and implementation.
- A successful CI build only confirms compilation; it does not prove that features work on a physical phone.

## Implementation rule
Build and test incrementally. Label unverified data honestly, prioritize correct routing and driver safety over decorative map features, and do not claim a feature is complete until it has been tested.
