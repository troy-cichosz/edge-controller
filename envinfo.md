# Development Environment Reference

This document contains temporary, ChatGPT-facing information specific to the user's current development, build, lab, and deployment environment. It is not platform architecture, project history, sprint status, or service documentation.

This file is intentionally environment-specific and must be removed or replaced before release/completion when no longer needed.

## Repository and Source Workflow

- GitHub organization/owner: `troy-cichosz`
- Primary project repository: `edge-controller`
- Development branch used for ChatGPT changes: `chatgpt`
- Last known-good mirrored baseline: `public`
- ADO/on-prem build and deployment system is user-controlled and is not directly accessible to ChatGPT.
- ADO state is authoritative for operational troubleshooting until it is mirrored to GitHub.

## Current Repositories

- `edge-controller`: `https://github.com/troy-cichosz/edge-controller`
- `edge-time`: `https://github.com/troy-cichosz/edge-time`
- `edge-audio`: `https://github.com/troy-cichosz/edge-audio`
- `edge-video`: `https://github.com/troy-cichosz/edge-video`
- `edge-gps`: `https://github.com/troy-cichosz/edge-gps`

## Current Development Hosts

| Logical role | Current environment-specific value |
|---|---|
| Controller/time authority host | `spoo-lin.spoocannon.com` |
| Controller host short name | `spoo-lin` |
| Controller API address | `10.10.11.111:8080` |
| Primary edge node | `pi4SSD` |
| Secondary edge node | `pi4nVME` |
| Controller deployment path | `/data/services/edge-controller` on `spoo-lin` |
| Container registry | `docker.spoocannon.com:5000` |

These values describe the current lab deployment only. They must not be treated as platform requirements or embedded as fixed values in generic code or documentation.

## Current Service Placement

```text
spoo-lin
+-- edge-controller
+-- edge-time authority

pi4SSD
+-- edge-audio
+-- edge-gps
+-- edge-time
+-- edge-video

pi4nVME
+-- edge-audio
+-- edge-gps
+-- edge-time
+-- edge-video
```

The service list is a current deployment snapshot, not a hard-coded architecture rule.

## Network and Naming

- Current DNS/domain suffix: `spoocannon.com`
- Current controller node host-resolution configuration:
  - `EDGE_NODE_HOST_MODE=auto`
  - `EDGE_NODE_DOMAIN=spoocannon.com`
- The controller attempts short-name resolution first and then the configured FQDN where applicable.
- Cross-service HTTP must use the hosting node hostname/IP and exposed host port, never Docker container/service names.
- Current host-addressed edge-time example: `http://pi4SSD.spoocannon.com:8095/health`

### Current Lab Network Values

| Role | Current environment-specific value |
|---|---|
| Primary AD/DC | `spoo-ds1` - `10.10.11.1` |
| Secondary AD/DC | `spoo-ad2` - `10.10.11.2` |
| Pi-hole management instances | `10.10.11.251`, `10.10.11.252` |
| Pi-hole VLAN 76 addresses | `10.10.76.1`, `10.10.76.2` |
| Guest network | VLAN 666 / `172.16.66.1` |
| Cowrie honeypot | VLAN 76 / `10.10.76.10` |

These network values are lab-specific references for troubleshooting and deployment. They are not architecture requirements.

## Hardware and Operating Environment

### Development Workstation

- Primary development workstation: Windows 11 with Zorin OS Pro dual boot.
- Primary AI GPU: NVIDIA RTX 3060 12 GB.
- Additional available GPUs: GTX 1080 and Quadro P1000.
- Ollama is currently located on the Windows `D:` drive.
- Stable Diffusion WebUI is currently located at `B:\AI`.

### Server and Storage

- Storage/CPU server: HP DL360 Gen9.
- Additional storage/server platform: Rock64 Pro running Armbian Trixie.
- Current controller host is a Linux VM named `spoo-lin`.

### Raspberry Pi Edge Devices

- Raspberry Pi edge devices currently used: Pi 4 units named `pi4SSD` and `pi4nVME`.
- The Pi devices currently lack a CMOS RTC; GNSS and edge-time are therefore relevant to the current temporal environment.

## Edge-Video Current Lab Details

- Camera hardware currently detected as Sony OV5647-class Raspberry Pi camera.
- Current native sensor mode observed: 2592x1944, 10-bit GBRG.
- Current capture device observed on at least one Pi: `/dev/video0`.
- Current operational recording test configuration has included 1920x1080, 30 FPS, 8,000,000 bitrate, and 60-second H.264 segments.
- Current evidence paths inside the edge-video container:
  - `/evidence/video`
  - `/evidence/manifests`
- Current edge-video health port convention: `8090` unless overridden by environment.

These are current test/deployment values, not universal service defaults or architectural requirements.

## Edge-Audio Current Lab Details

- Current microphone hardware: INMP441/AITRIP omnidirectional I2S microphone modules.
- Current Pi audio configuration observed: ALSA `plughw:3,0`, 48 kHz stereo, `S32_LE`.
- Current audio deployment uses controller registration and local metadata/evidence storage.
- Current metadata bind/storage arrangement includes the service metadata directory mapped to `/metadata` in the container and a host-side metadata location under `/data/services/metadata`.

## Edge-GPS Current Lab Details

- Current GNSS receiver modules: GY-GPS6MV2.
- GPS work is currently paused while edge-video and temporal evidence integration proceed.
- Previous Pi serial troubleshooting included missing `/dev/serial0`, `/dev/ttyAMA*`, and `/dev/serial*` devices and a `console=ttyS0` kernel-command-line entry.

## Edge-Time Current Lab Details

- Current time-authority host: `spoo-lin.spoocannon.com`.
- Current edge-time agents run on `pi4SSD` and `pi4nVME`.
- Current observed edge-time service endpoint example uses host port `8095`.
- Current registered edge-time hosts include `pi4SSD`, `pi4nVME`, and `spoo-lin.spoocannon.com`.
- The current edge-time registration exposes resources including health, status, time, sources, attestation, authority, and authority-time.
- Current edge-time work is concerned with local temporal authority, holdover, synchronization state, and temporal provenance; these environment details do not define the permanent service contract.

## Controller Database and Runtime Notes

- Controller uses PostgreSQL 17 in the current environment.
- Current controller API port: `8080`.
- Current controller database/service deployment is containerized.
- Current controller deployment path is `/data/services/edge-controller` on `spoo-lin`.
- Current node registrations include `pi4SSD`, `pi4nVME`, and `spoo-lin.spoocannon.com`.

## Temporary Environment-Only Data Policy

Environment-specific values belong here when they are useful to reconstruct the user's lab, development, build, or deployment context.

Other project documents should use placeholders such as:

```text
<CONTROLLER_HOST>
<CONTROLLER_HOSTNAME>
<CONTROLLER_API_HOST>:<CONTROLLER_API_PORT>
<EDGE_NODE_ID>
<EDGE_NODE_HOSTNAME>
<DOMAIN>
<REGISTRY_HOST>:<REGISTRY_PORT>
<DEPLOYMENT_PATH>
<HOST_PORT>
<HOST_PATH>
<CONTAINER_PATH>
<IP_ADDRESS>
```

When a value is merely an architectural example, keep it generic rather than moving it here. When a value identifies the user's actual host, network, hardware, path, port, deployment, or current runtime state, treat it as environment-specific.

Do not move architectural rules, service contracts, generic examples, project history, or current sprint state into this file merely because they mention an environment concept.
