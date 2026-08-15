# Mammotion — Home Assistant Integration (fork)

A fork of [mikey0000/Mammotion-HA](https://github.com/mikey0000/Mammotion-HA) carrying two changes
for **cloud-only setups without Bluetooth coverage**. Everything else is upstream's work.

> **Most people should install [the original](https://github.com/mikey0000/Mammotion-HA) instead.**
> This fork is a hobby effort, tested against a single Luba 1 running cloud-only, with no support.

## Is this for you?

Worth trying if **both** apply:

- No usable Bluetooth connection between the mower and Home Assistant.
- The mower works for a few hours, then stops responding to commands and recovers by itself much
  later.

If Bluetooth works for you, this fork gains you nothing — both changes are inert over Bluetooth.

## What differs from upstream

**Staying under the cloud send quota.** A device is allowed 600 outbound cloud messages per rolling
12-hour window; exhausting it blocks every send for hours. Two code paths burned that budget during
a single mow because both fired on mower status changes, which oscillate constantly while mowing.
This fork holds one continuous report stream while the mower is active, renewed just inside the
device's window, so a whole mow costs about one message per five minutes. The rate-limit error is
also handled properly instead of surfacing as tracebacks and triggering a pointless re-login.

Mowers on firmware 1.30.25.1 or newer have no send quota at all, so this change is inert there.

**`job_paused` sensor (Luba 1 only).** A diagnostic binary sensor showing whether the mower holds a
resumable job in memory. On Luba 1 a paused job keeps its breakpoint until the mower is sent back
out, unlike Luba 2 and Yuka — so this stays on while the mower sits in the dock with unfinished
work, which its normal state does not reveal.

## Setup

For prerequisites, supported hardware, map offsets, companion dashboard plugins and troubleshooting,
see upstream's [README](https://github.com/mikey0000/Mammotion-HA#readme) and
[wiki](https://github.com/mikey0000/Mammotion-HA/wiki/Getting-Started). This fork does not duplicate
them, so they cannot go stale here.

Remove the upstream integration first if you have it — both use the `mammotion` domain and cannot
coexist.

## Credits

Essentially all of this code is by [mikey0000](https://github.com/mikey0000) and the
[Mammotion-HA contributors](https://github.com/mikey0000/Mammotion-HA/graphs/contributors). The send
quota change originates from [jirkaorlik-hash](https://github.com/jirkaorlik-hash). Communication
with mowers goes through the [PyMammotion](https://github.com/mikey0000/PyMammotion) library.
