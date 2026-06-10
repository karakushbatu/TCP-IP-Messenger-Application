# TCP Tactical Messenger — Test Plan

## Unit Test Scenarios

| ID | Scenario | Module |
|---|---|---|
| UT-01 | Message 1 pack/unpack roundtrip | serializer |
| UT-02 | Message 2 pack/unpack roundtrip | serializer |
| UT-03 | Message 1 payload size = 64 bytes | serializer |
| UT-04 | Message 2 payload size = 29 bytes | serializer |
| UT-05 | Length header correctness | serializer |
| UT-06 | UTF-8 Turkish character encoding | serializer |
| UT-07 | Null padding correctness | serializer |
| UT-08 | Reject string > 25 bytes | serializer |
| UT-09 | Boundary min/max validation | validator |
| UT-10 | Unknown message ID | serializer |
| UT-11 | Corrupt/truncated payload | serializer |
| UT-12 | Auto-response mapping | auto_response |
| UT-13 | Loop prevention guard | auto_response |

## Integration Test Scenarios

| ID | Scenario |
|---|---|
| IT-01 | Server starts on localhost |
| IT-02 | Client connects to server |
| IT-03 | Client sends Message 1, server receives |
| IT-04 | Auto-response Message 1 → Message 2 |
| IT-05 | Unknown message produces warning event |
| IT-06 | Disconnect produces disconnected event |

## Manual System Test Scenarios

| ID | Scenario |
|---|---|
| ST-01 | Launch app and use automatic server-client demo mode |
| ST-02 | Send Message 1 manually and verify Message 2 auto-response |
| ST-03 | Send Message 2 manually and verify Message 1 auto-response |
| ST-04 | Enable periodic Message 1 sending at 100 ms |
| ST-05 | Enable periodic Message 2 sending at 500 ms |
| ST-06 | Try invalid field values and verify send button is disabled |
| ST-07 | Send unknown Message ID 99 and verify warning |
| ST-08 | Send corrupt/truncated payload and verify error handling |
| ST-09 | Disconnect peer and verify status update |
| ST-10 | Run 2-minute demo without crash or UI freeze |

## Traceability Matrix

| Requirement | Tests |
|---|---|
| Binary serialization | UT-01–UT-08, IT-03 |
| Validation | UT-09, ST-06 |
| Auto-response | UT-12, IT-04, ST-02, ST-03 |
| Loop prevention | UT-13 |
| Unknown messages | UT-10, IT-05, ST-07 |
| Corrupt messages | UT-11, ST-08 |
| TCP framing | UT-05, framing tests |
| Periodic sending | ST-04, ST-05 |
| Multi-instance demo | ST-01 |
| Disconnect handling | IT-06, ST-09 |
