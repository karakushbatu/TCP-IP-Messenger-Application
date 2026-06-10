# Protocol Bridge — Protocol Specification

## Application Purpose

**Protocol Bridge** is a desktop demonstration application for TCP/IP binary messaging. It supports two predefined message types, automatic cross-response, periodic transmission, multi-instance tabs, and strict field validation.

## TCP Framing Rule

Every message on the wire uses length-prefix framing:

```
[4-byte length header][binary message payload]
```

- Header format: `!I` (unsigned int, network byte order, big-endian)
- Length value = payload size only (excludes the 4-byte header)
- Receiver must read exactly `length` bytes after the header

## Message 1 — Personnel Message (64 bytes)

| Field | Internal Name | Type | Size | Constraint |
|---|---|---:|---:|---|
| Message ID | message_id | int32 | 4 | fixed `1` |
| Unit Reference No | unit_reference_no | int32 | 4 | `-1000` to `9999` |
| First Name | first_name | string | 25 | UTF-8, null-padded |
| Unit No | unit_no | uint32 | 4 | `0` to `4294967295` |
| Last Name | last_name | string | 25 | UTF-8, null-padded |
| Rank | rank | int16 | 2 | `0=Üsteğmen`, `1=Teğmen`, `2=Asteğmen` |

Struct format: `!ii25sI25sh`

## Message 2 — Unit Position Message (29 bytes)

| Field | Internal Name | Type | Size | Constraint |
|---|---|---:|---:|---|
| Message ID | message_id | int32 | 4 | fixed `2` |
| Unit Reference No | unit_reference_no | int32 | 4 | `1` to `9999` |
| Position Valid | position_validity | byte | 1 | `1=True`, `0=False` |
| Latitude | latitude | int64 | 8 | `-32400000` to `32400000` |
| Longitude | longitude | int64 | 8 | `-64800000` to `64800000` |
| Altitude | altitude | int32 | 4 | `0` to `10000` |

Struct format: `!iibqqi`

## Validation Constraints

- All integers must be within defined ranges
- String fields validated by UTF-8 byte length (max 25 bytes)
- Message ID must match the selected message type
- Invalid messages cannot be sent from the UI (Send button disabled)

## Auto-Response Behavior

- Receiving Message 1 → automatically sends Message 2
- Receiving Message 2 → automatically sends Message 1
- Loop prevention: suppression after auto-send prevents ping-pong
- Auto-response is toggleable from the UI (Auto Reply switch)
- Auto-response messages are tagged `[Auto]` in logs

## Server Connection Policy

- Each server instance accepts **one active TCP client** at a time
- When a new client connects, the previous client is disconnected at the socket level
- UI status indicators must reflect disconnect for the replaced client

## Unknown / Corrupt Message Behavior

- Unknown message ID → warning event, no auto-response, no crash
- Truncated/corrupt payload → protocol error event, no auto-response, no crash
