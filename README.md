# Mammotion-HA — fork

A fork of [mikey0000/Mammotion-HA](https://github.com/mikey0000/Mammotion-HA), the Home Assistant
integration for Mammotion robot lawn mowers.

This fork exists to carry two changes aimed at **cloud-only setups without Bluetooth coverage**.
Everything else is upstream's work, tracked and merged in periodically.

> **Most people should install [the original](https://github.com/mikey0000/Mammotion-HA), not this.**
> This fork is maintained as a hobby, tested against exactly one mower (a Luba 1 running cloud-only),
> and comes with no support. It is only worth using if you recognise your own setup below.

## Is this fork for you?

Probably, if **both** of these are true:

- Your mower has no usable Bluetooth connection to Home Assistant — no proxy in range, or you run
  the integration purely over the cloud.
- Your mower goes unresponsive after working fine for a few hours, and recovers on its own much
  later. Commands stop reaching it; entities go stale or unavailable.

Probably not, if you have Bluetooth working. Both changes here are no-ops or near no-ops on
Bluetooth, so you would gain nothing.

## What is different from upstream

### 1. Staying under the cloud send quota

The Mammotion library allows a device 600 outbound cloud messages per rolling 12-hour window. Once
that budget is exhausted, *every* send is blocked for hours — which is what makes the mower appear
to connect, work for a while, and then die.

On a cloud-only setup, two code paths spent that budget during a single mow, because both were
driven by the mower's status changing, and status oscillates constantly while mowing:

- the report coordinator requested a fresh snapshot on every status transition
- the error coordinator issued two reads on every entry into working, returning, lock or pause

This fork replaces per-transition polling with a single continuous report stream, held only while
the mower is in an active mode and renewed on a 270-second timer, just inside the device's
300-second window. The mower then pushes state every few seconds at no cost to the quota. A whole
mow costs roughly one send per five minutes instead of one or three per transition. Leaving active
mode stops the stream and takes one debounced snapshot to capture the settled state.

The error coordinator's reads are debounced to at most once per ten minutes.

Separately, the rate-limit error itself is now handled. It previously surfaced as raw tracebacks,
and was partly treated as an authentication problem — triggering a pointless re-login, since a send
quota has nothing to do with credentials. The device now degrades to offline cleanly.

**Note on firmware:** mowers running firmware **1.30.25.1 or newer** have migrated to a different
Mammotion broker and have no send quota at all. On those, this change is simply inert. It matters
for older firmware, which is where Luba 1 owners tend to be.

Bluetooth users are unaffected — the report stream is free over Bluetooth, and active-mode telemetry
already flows through the Bluetooth polling loop.

The work behind this change comes from [jirkaorlik-hash's fork](https://github.com/jirkaorlik-hash/Mammotion-HA);
see [Credits](#credits).

### 2. `job_paused` binary sensor (Luba 1 only)

A diagnostic binary sensor exposing whether the mower is holding a resumable job in memory.

On Luba 1, a job that is paused — manually, or by returning to the dock mid-job — keeps a stored
breakpoint until the mower is sent back out and actually reaches that point. This differs from
Luba 2 and Yuka, where the paused state clears immediately. The sensor reads that stored breakpoint
directly, so it stays on while the mower sits in the dock with an unfinished job, which the mower's
regular state does not tell you.

Useful for automations along the lines of "if it stopped to charge mid-job, send it back out once
charged". The entity is only created for Luba 1 hardware.

Currently named "Job paused" in every language; translations for the other locales are not done yet.

## Installation

Via [HACS](https://hacs.xyz/) as a custom repository:

1. In HACS, open the three-dot menu and choose **Custom repositories**.
2. Repository: `https://github.com/terjefl/Mammotion-HA`
3. Category: **Integration**, then **Add**.
4. Search for "Mammotion" in HACS and install it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & Services → + Add Integration** and configure Mammotion.

If you already have the upstream integration installed, remove it first — both use the same
`mammotion` domain and cannot coexist.

## Documentation

This fork does not duplicate upstream's documentation, which would only go stale. For setup,
prerequisites, supported hardware, map offsets, companion dashboard plugins and troubleshooting,
see upstream:

- [Upstream README](https://github.com/mikey0000/Mammotion-HA#readme)
- [Getting started (wiki)](https://github.com/mikey0000/Mammotion-HA/wiki/Getting-Started)

## Relationship to upstream

This fork tracks `mikey0000/Mammotion-HA` and merges new upstream releases as they appear. It is not
a competing project and is not trying to become one.

Neither change here has been proposed upstream. If you hit a bug, work out first whether it is in
this fork's changes or in the integration generally — if it is the latter, upstream is the right
place, and please report it there rather than here.

Currently based on upstream `0.6.4-beta12`.

## Credits

Essentially all of this code is written by [mikey0000](https://github.com/mikey0000) and the
[contributors to Mammotion-HA](https://github.com/mikey0000/Mammotion-HA/graphs/contributors). This
fork adds two changes on top of their work.

The cloud send quota change originates from [jirkaorlik-hash](https://github.com/jirkaorlik-hash),
and is used here unmodified.

The integration communicates with mowers through the
[PyMammotion](https://github.com/mikey0000/PyMammotion) library.

[![Contributors](https://contrib.rocks/image?repo=mikey0000/Mammotion-HA)](https://github.com/mikey0000/Mammotion-HA/graphs/contributors)
