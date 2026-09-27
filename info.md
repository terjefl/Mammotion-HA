# Mammotion — Home Assistant Integration (fork)

A fork of [mikey0000/Mammotion-HA](https://github.com/mikey0000/Mammotion-HA) carrying a change
for setups where the mower **spends its working hours out of Bluetooth range** and falls back to the
cloud while mowing, plus two smaller fixes. Everything else is upstream's work.

> **Most people should install [the original](https://github.com/mikey0000/Mammotion-HA) instead.**
> This fork is a hobby effort, tested against one Luba 1 and one Yuka, with no support.

## Is this for you?

Worth trying if **both** apply:

- The mower reaches Home Assistant over the cloud while out mowing — either no Bluetooth at all, or,
  more commonly, a proxy that only covers the dock area.
- It works for a few hours, then stops responding to commands and recovers by itself much later.

Partial coverage is the worst case: the quota is spent while the mower is out working, beyond the
proxy's reach and changing status constantly. In the dock it costs nothing.

If the mower stays within Bluetooth reach while it works, this fork gains you nothing — the cloud
request is skipped whenever a Bluetooth stream is running. That applies to a proxy covering the
whole lawn, and to the neatest fix of all, which some owners use: fitting an ESPHome Bluetooth proxy
to the mower itself so coverage travels with it.

## Status

**Use at your own risk.** I intend to keep this roughly in sync with upstream but do not promise it
— this fork serves my own setup, and that decides when it gets attention. No support, no release
schedule. If that does not suit you, the original is actively maintained and is the better choice.

## What differs from upstream

**Staying under the cloud send quota.** A device is allowed 600 outbound cloud messages per rolling
12-hour window; exhausting it blocks every send for hours. Two code paths burned that budget during
a single mow because both fired on mower status changes, which oscillate constantly while mowing.
This fork holds one continuous report stream while the mower is active, renewed just inside the
device's window, so a whole mow costs about one message per five minutes. A background refresh that
hits the quota degrades the device to offline quietly instead of raising an error.

Mowers on firmware 1.30.25.1 or newer have no send quota at all, so this change is inert there.

**`job_paused` sensor (Luba 1 only).** A diagnostic binary sensor showing whether the mower holds a
resumable job in memory. On Luba 1 a paused job keeps its breakpoint until the mower is sent back
out, unlike Luba 2 and Yuka — so this stays on while the mower sits in the dock with unfinished
work, which its normal state does not reveal.

**Area switches for deleted areas are removed.** Areas deleted on the mower could keep their switch
in Home Assistant, and mowing one failed with "Invalid task area detected". Area switches are now
checked against the mower's own area list.

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
