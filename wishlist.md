# WISH LIST

The following are desired future capabilities.

They are **not current implementation commitments** unless deliberately promoted into the roadmap.

All available collected information from any and all devices, video, recordings, gps data, etc. from a specific time can be presented and synced for playback on some device (ie. cell phone, web page, etc.)
All information collected has as much evendentiary confidnece as possible with the intent of introduction in a civil, criminal and/or traffic trial/hearing.
All devices/services sync time to an authority to help in syncing video to audio, GPS location, etc. 
GPS locations are presented on a map
GUI/APP can adjust and calibrate settings on any service, connected device, etc.  
Multiple types and numbers of Video devices are supported
Audio information can be used along with GPS to try and pinpoint locations of speakers, vehicles, and other noises.
Video devices may be used to create 3d/VR files (ie. steroscopic video)
Support various sensors modules  (ie. laser, reed, buttons) for data collection, triggering, and whatever information for event recreation/presentations (ie. this door was opened at, distances between objects are determined, etc.)
Source audio and video is preserved on devices initially, both proccessed and copied to a central store (ie. PC or webendpoint running the controller) for as close to real time presentation and correlation as possible and reasonable, as well as for backup purposes.
AI backend to process, correlate, analyze, transcribe, research, respond via text and audio, etc.
Audio service also supports playback of sound on devices that support it (ie. from gui/app, playback a source file and/or a sound file and/or AI response, etc.)
A service/device that can scan for any and all detectable devices (ie. wifi, bluetooth, cell phones), capture as much information from them and treat as evidence. 
This scan service should also support attempting to connect to any open public network for backend/remote communication to AI and internet.
AI should be legal based and trained accordingly to know state and federal law, Understand proceedual and consitutional law, Black Law dictonary access and preference, etc. 
Host Devices (currently PIs) will connect to a controller network (host running locally) by default but attempt to connect to open or defined network fallbacks as well (I think this would be in a scan/network service)  
OBD2 integration to pull data from vehicle like speed, warning/trouble codes, etc. to prove status of vehicle (ie. stopped for headlight out but no trouble/fault code from car, etc.)
All services that retain data (ie. video, audio. manifests, etc.) should have a controller/gui based "purge" option for testing and data cleanup. Ie. a button on each service to purge all collected data and a master button in the gui to purge all data from all reporting services.

This should grow into a generic platform data-lifecycle capability with service-owned purge definitions and controller-managed orchestration. Desired future scopes include:

- Development reset of one selected node or all nodes to a clean disposable-data state.
- Service-specific purge of selected data classes without affecting unrelated services.
- Explicit data classes such as recordings, manifests, derived/live media, logs, metadata, caches, runtime state, and other service-owned disposable data.
- Preservation of configuration and deployment state during ordinary data purges.
- Clear separation between ordinary data purge, service-state reset, node data reset, and eventual factory/identity reset.
- Capability-driven service declarations so the controller does not contain hard-coded knowledge of service-specific filesystem paths.
- GUI controls for selected-node and fleet-wide purge operations with explicit confirmation and operation results.
- Controller APIs for querying purgeable data classes and executing approved purge operations.
- Service-owned purge handlers so each service remains responsible for safely identifying and removing its own data.
- Auditable management records for purge operations once evidence-affecting administrative audit logging is implemented.
- Production-safe retention/deletion policy and authorization before real evidence is subject to remote purge.
- Self-healing/recovery behavior for service state corruption where safe, with explicit integrity boundaries rather than silently rewriting authoritative evidence.

## Evidence Reconstruction

```text
All available information from any/all devices,
video, audio, GPS, vehicle telemetry, sensors, etc.
for a selected time/event can be synchronized
and presented on a phone, browser, or other device.
```

## Evidentiary Confidence

```text
Preserve as much technical evidence confidence,
integrity, provenance, repeatability, and verifiability
as reasonably possible for potential civil, criminal,
traffic, or administrative proceedings.
```

This remains a technical engineering objective and does not guarantee admissibility.

## Common Time

```text
All evidence-producing devices/services synchronize
to a common authority and preserve enough timing context
to correlate video, audio, GPS, vehicle telemetry,
and sensor information.
```

## Mapping

```text
GPS locations and trajectories presented on maps.
```

## Universal GUI / App Configuration

```text
Configure and calibrate services, devices,
sensors, cameras, audio sources, and other components
from a unified GUI/application.
```

## Multiple Video Sources

```text
Multiple camera types
Multiple cameras
Independent camera identities
Synchronized multi-camera presentation
```

## Audio/Location Analysis

```text
Use audio together with GPS, timing, multiple microphones,
and other evidence to estimate the locations of speakers,
vehicles, and other sounds.
```

Results must preserve uncertainty and source information.

## 3D / VR

```text
Stereoscopic video
3D reconstruction
VR presentation
multi-camera scene reconstruction
```

## General Sensor Framework

Potential sensors:

```text
laser
distance
reed switches
buttons
door sensors
impact sensors
motion sensors
environmental sensors
other future modules
```

Sensors may support:

```text
data collection
event triggering
state reconstruction
distance determination
object/door state
event presentation
```

## Local + Central Evidence

```text
Preserve original audio/video/evidence locally.

Copy verified evidence to a central system when
reasonable for near-real-time presentation,
correlation, backup, indexing, or AI processing.
```

The local authoritative copy remains preserved.

## AI Backend

```text
process
correlate
analyze
transcribe
OCR
computer vision
research
respond by text
respond by audio
generate reports
```

## Audio Playback

The audio service may eventually support controlled playback of:

```text
source recordings
sound files
generated audio
AI responses
```

## Device Discovery

A future service may detect nearby:

```text
Wi-Fi devices
Bluetooth devices
other detectable technologies
```

and preserve relevant observations where technically and legally appropriate.

## Network Connectivity Assistance

A future service may detect available networks and assist with legitimate connectivity for:

```text
backend communication
AI access
internet access
remote synchronization
```

Connection attempts must remain subject to authorization and applicable law.

## Vehicle Telemetry

Future OBD-II/vehicle integration:

```text
speed
RPM
fault codes
vehicle identity
vehicle state
diagnostics
other available telemetry
```

## Cryptographic Evidence Infrastructure

Potential future capabilities:

```text
signed manifests
device certificates
hash chains
Merkle structures
independent verification tools
external trusted timestamping
key rotation
trust anchors
```

## Evidence Custody

```text
collection history
copy history
transfer history
verification history
analysis history
derivative history
export history
```

## Presentation Watermark

Generate a clearly identified derivative/presentation copy with:

```text
timestamp
GPS
speed
camera/source
evidence ID
event ID
```

Never rely on the watermark as the primary integrity mechanism.

Never modify authoritative source evidence merely to add the watermark.

---

# 38. Guiding Principle

The project should ultimately transform:

```text
"I have a recording."
```

into:

```text
"I have an evidence object whose content,
device/source identity, capture time,
time-source provenance, uncertainty,
location, configuration, calibration state,
event relationships, and cryptographic integrity
can be independently examined."
```

Everything else should support that objective, enable it, or be deliberately deferred.

---