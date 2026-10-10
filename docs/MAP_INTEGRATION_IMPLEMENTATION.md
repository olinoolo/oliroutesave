# OLI RouteSave — Map integration implementation notes

This document is the implementation checklist for the first real-map milestone. It is not evidence that the feature is already in the APK.

## Keep map rendering and routing separate

- MapLibre Native Android renders the map. It needs a compatible style URL and a licensed source of map data/tiles. A map renderer alone does not provide geocoding, routes, traffic, or truck restrictions.
- A routing provider returns the road geometry, distance, travel-time estimate and any supported truck restriction warnings.
- Do not draw a straight line between two addresses and label it as a road route.
- Do not show example/default kilometres as if they were calculated.

## Phase 1 — map-only proof of concept

1. Inspect the existing Android Gradle plugin, Kotlin, Compose and minimum Android versions before selecting a MapLibre dependency version.
2. Add the MapLibre Native Android dependency compatible with those versions.
3. Add a dedicated Compose map host that owns the native map view lifecycle. Ensure it is created once, resumes/pauses with the screen lifecycle, and is destroyed safely.
4. Use a real, licensed style URL; never assume the public OpenStreetMap tile servers are a production tile service.
5. Show a loading state and a readable error when style/data cannot load.
6. Test on a physical Android phone with Wi-Fi/mobile data, then test network loss and screen rotation.

Acceptance criteria: a real interactive map renders and pans/zooms without crashing; loading and network failures are visible; no fake route, ETA or distance is displayed.

## Phase 2 — location

1. Request foreground location permission only when the user invokes the location feature.
2. Explain the purpose in Slovak and handle denial or approximate location without crashing.
3. Show the user's location only when permission is granted and a fresh location is available.
4. Do not enable background tracking as part of the first map milestone.

Acceptance criteria: allow, deny, and revoke permission paths all work; the map still opens when permission is denied.

## Phase 3 — place search and real route

1. Select and document the geocoding service, pricing, data retention and European coverage before adding a search API.
2. Let the user choose among ambiguous search results; distinguish company office, warehouse/site and truck entrance when data supports it.
3. Send selected coordinates to a real routing endpoint and draw the returned road geometry.
4. Display distance and ETA only from the response, with units and a clear network/provider error state.
5. Calculate fuel cost using the saved vehicle consumption and fuel price, and identify the estimate as an estimate.

## Phase 4 — truck safety gate

Before calling a route truck-safe, verify that the selected provider and account support the exact vehicle restrictions needed: height, width, length, gross weight, axle information and applicable ADR/tunnel parameters. Check the service's regional coverage. If a restriction is missing or unknown, say so clearly; absence of a mapped restriction is not proof of safe passage.

## Credentials and privacy

- Never commit a private API key to Git or bake an unrestricted key into the APK.
- Use provider-supported key restrictions. If secret credentials are needed, put them behind a small backend rather than distributing a server secret in the app.
- Review provider terms, billing limits, attribution requirements and data policies before production.
- Do not send or store a user's precise location beyond what is needed for the explicitly requested feature.

## Test matrix

- Fresh install; app reopen; screen rotation.
- Online, slow connection and offline.
- Location allowed, denied and revoked.
- Map style fails to load.
- Search returns no results, one result and ambiguous results.
- Route request succeeds, times out, returns no route or lacks truck restriction data.
- Distance/ETA are absent unless a successful route response provides them.
