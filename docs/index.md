# GLaDOS OPC UA server reference

Generated from `config/` by `python -m glados_opcua.docs`. Package version **2.0.0**.
Do not edit by hand: edit configuration or code, then regenerate.

> This server is a communication layer, not a safety system. Interlocks,
> emergency stops and motion validation must remain in independent
> safety-rated systems.

## Server

| Setting | Value |
|---|---|
| Profile | `legacy` |
| Endpoint | `opc.tcp://0.0.0.0:4840/server/` |
| Server name | `DTL Local OPC UA Server Test` |
| Application URI | `urn:freeopcua:python:server` |
| Bind override | `from endpoint:from endpoint` |
| Objects | 18 |
| Variables | 488 |
| Writable variables | 482 |
| Health namespace | disabled |
| Permissions enforced | no |

## Security posture

| Setting | Value |
|---|---|
| Policies | `NoSecurity` |
| Identity tokens | `Anonymous` |
| Anonymous allowed | yes |
| Insecure legacy acknowledged | yes |
| Server certificate | `certificates/server.pem` |
| Configured users | 0 |

Production requires `Basic256Sha256_SignAndEncrypt` or stronger, configured
users with `password_env`/client certificates, and `permissions.enforced: true`.
The legacy profile disables password validation by design and must be isolated.

## Namespaces

| Index | URI | Kind | Description |
|---|---|---|---|
| 0 | `http://opcfoundation.org/UA/` | standard |  |
| 1 | `urn:freeopcua:python:server` | application | Application namespace; hosts the legacy Operator object |
| 2 | `urn:glados:opcua:communication` | equipment |  |
| 3 | `urn:glados:opcua:magnetee` | equipment |  |
| 11 | `urn:glados:opcua:printer1` | equipment |  |
| 12 | `urn:glados:opcua:printer2` | equipment |  |
| 13 | `urn:glados:opcua:printer3` | equipment |  |
| 14 | `urn:glados:opcua:printer4` | equipment |  |
| 21 | `urn:glados:opcua:robot1` | equipment |  |
| 22 | `urn:glados:opcua:robot2` | equipment |  |
| 23 | `urn:glados:opcua:robot3` | equipment |  |
| 24 | `urn:glados:opcua:robot4` | equipment |  |
| 29 | `urn:glados:opcua:robotdog1` | equipment |  |
| 31 | `urn:glados:opcua:camera1` | equipment |  |
| 41 | `urn:glados:opcua:airpurifier1` | equipment |  |
| 42 | `urn:glados:opcua:airpurifier2` | equipment |  |
| 51 | `urn:glados:opcua:glove1` | equipment |  |
| 52 | `urn:glados:opcua:glove2` | equipment |  |
| 53 | `urn:glados:opcua:rgb-leds` | equipment |  |

Indexes [4, 5, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 20, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 43, 44, 45, 46, 47, 48, 49, 50, 54] are reserved placeholders (`urn:glados:opcua:reserved:<index>`) so numeric
indexes never shift. Health index 54 is registered when health is enabled.

## Equipment

| Object | Namespace | NodeId | Variables | Writable | Description |
|---|---|---|---|---|---|
| Communication | 2 | `ns=2;i=1` | 1 | 1 | Legacy communication group (LabCount, wrapperDisconnect) |
| Operator | 1 | `ns=1;i=2001` | 1 | 1 | Legacy operator group |
| MagnetEE | 3 | `ns=3;i=1` | 2 | 2 | Magnet end-effector controller |
| robot1 | 21 | `ns=21;i=1` | 61 | 61 | KUKA KMR iiwa 14 R820 |
| robot2 | 22 | `ns=22;i=1` | 67 | 61 | KUKA KMR iiwa 14 R820 |
| robot3 | 23 | `ns=23;i=1` | 62 | 62 | KUKA KMR iiwa 14 R820 |
| robot4 | 24 | `ns=24;i=1` | 63 | 63 | FlexFellow iiwa 14 R820 |
| Printer1 | 11 | `ns=11;i=1` | 30 | 30 | Creality Ender 3 v2 |
| Printer2 | 12 | `ns=12;i=1` | 30 | 30 | Creality Ender 3 v2 |
| Printer3 | 13 | `ns=13;i=1` | 30 | 30 | Creality Ender 3 v2 |
| Printer4 | 14 | `ns=14;i=1` | 30 | 30 | Creality Ender 3 v2 |
| Camera1 | 31 | `ns=31;i=1` | 8 | 8 | JAI camera |
| RobotDog1 | 29 | `ns=29;i=1` | 62 | 62 | Quadruped robot dog |
| AirPurifier1 | 41 | `ns=41;i=1` | 11 | 11 | Air purifier (Perry) |
| AirPurifier2 | 42 | `ns=42;i=1` | 11 | 11 | Air purifier (Kermit) |
| Glove 1 (Left) | 51 | `ns=51;i=1` | 7 | 7 | Haptic glove, left |
| Glove 2 (Right) | 52 | `ns=52;i=1` | 7 | 7 | Haptic glove, right |
| 500 RGB LEDs | 53 | `ns=53;i=1` | 5 | 5 | LED strip controller |

## Node reference

Browse names use namespace 0 unless stated otherwise. NodeIds are exact and
include legacy punctuation such as trailing semicolons.

### Communication

Object NodeId `ns=2;i=1`, namespace `2`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| LabCount | `ns=2;s=LabCount` | Int32 | `0` | yes | unverified | admin |

- **LabCount**: Communication counter ownership unconfirmed

### Operator

Object NodeId `ns=1;i=2001`, namespace `1`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| wrapperDisconnect | `ns=1;s=wrapperDisconnect` | Boolean | false | yes | status | device |

### MagnetEE

Object NodeId `ns=3;i=1`, namespace `3`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| magCount | `ns=3;s=magCount` | Int32 | `0` | yes | unverified | admin |
| magInfo | `ns=3;s=magInfo` | String | `[a,b,c],[e,f,g],[h,i,j]` | yes | unverified | admin |

- **magCount**: naming convention does not establish an owner
- **magInfo**: naming convention does not establish an owner

### robot1

Object NodeId `ns=21;i=1`, namespace `21`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| R1d_Joi1 | `ns=21;s=R1d_Joi1;` | Double | `-15.0` | yes | telemetry | device |
| R1d_Joi2 | `ns=21;s=R1d_Joi2;` | Double | `39.0` | yes | telemetry | device |
| R1d_Joi3 | `ns=21;s=R1d_Joi3;` | Double | `1.0` | yes | telemetry | device |
| R1d_Joi4 | `ns=21;s=R1d_Joi4;` | Double | `-108.0` | yes | telemetry | device |
| R1d_Joi5 | `ns=21;s=R1d_Joi5;` | Double | `164.0` | yes | telemetry | device |
| R1d_Joi6 | `ns=21;s=R1d_Joi6;` | Double | `58.0` | yes | telemetry | device |
| R1d_Joi7 | `ns=21;s=R1d_Joi7;` | Double | `-82.0` | yes | telemetry | device |
| R1d_Tor1 | `ns=21;s=R1d_Tor1;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor2 | `ns=21;s=R1d_Tor2;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor3 | `ns=21;s=R1d_Tor3;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor4 | `ns=21;s=R1d_Tor4;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor5 | `ns=21;s=R1d_Tor5;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor6 | `ns=21;s=R1d_Tor6;` | Double | `0.0` | yes | telemetry | device |
| R1d_Tor7 | `ns=21;s=R1d_Tor7;` | Double | `0.0` | yes | telemetry | device |
| R1d_PosX | `ns=21;s=R1d_PosX;` | Double | `0.0` | yes | telemetry | device |
| R1d_PosY | `ns=21;s=R1d_PosY;` | Double | `0.0` | yes | telemetry | device |
| R1d_PosZ | `ns=21;s=R1d_PosZ;` | Double | `0.0` | yes | telemetry | device |
| R1d_RotA | `ns=21;s=R1d_RotA;` | Double | `0.0` | yes | telemetry | device |
| R1d_RotB | `ns=21;s=R1d_RotB;` | Double | `0.0` | yes | telemetry | device |
| R1d_RotC | `ns=21;s=R1d_RotC;` | Double | `0.0` | yes | telemetry | device |
| R1d_ForX | `ns=21;s=R1d_ForX;` | Double | `1.0` | yes | telemetry | device |
| R1d_ForY | `ns=21;s=R1d_ForY;` | Double | `1.0` | yes | telemetry | device |
| R1d_ForZ | `ns=21;s=R1d_ForZ;` | Double | `1.0` | yes | telemetry | device |
| R1d_MomX | `ns=21;s=R1d_MomX;` | Double | `0.0` | yes | telemetry | device |
| R1d_MomY | `ns=21;s=R1d_MomY;` | Double | `0.0` | yes | telemetry | device |
| R1d_MomZ | `ns=21;s=R1d_MomZ;` | Double | `0.0` | yes | telemetry | device |
| R1d_BaseX | `ns=21;s=R1d_BaseX;` | Double | `8.7` | yes | telemetry | device |
| R1d_BaseY | `ns=21;s=R1d_BaseY;` | Double | `9.7` | yes | telemetry | device |
| R1d_BaseA | `ns=21;s=R1d_BaseA;` | Double | `0` | yes | telemetry | device |
| R1d_Disconnect | `ns=21;s=R1d_Disconnect;` | Boolean | false | yes | telemetry | device |
| R1c_Connected | `ns=21;s=R1c_Connected;` | Boolean | true | yes | status | device |
| R1c_Start | `ns=21;s=R1c_Start;` | Boolean | false | yes | command | controller |
| R1c_ProgID | `ns=21;s=R1c_ProgID;` | Int32 | `0` | yes | command | controller |
| R1f_End | `ns=21;s=R1f_End;` | Boolean | false | yes | feedback | device |
| R1f_Ready | `ns=21;s=R1f_Ready;` | Boolean | false | yes | feedback | device |
| R1c_Joi1 | `ns=21;s=R1c_Joi1;` | Double | `0.0` | yes | command | controller |
| R1c_Joi2 | `ns=21;s=R1c_Joi2;` | Double | `0.0` | yes | command | controller |
| R1c_Joi3 | `ns=21;s=R1c_Joi3;` | Double | `0.0` | yes | command | controller |
| R1c_Joi4 | `ns=21;s=R1c_Joi4;` | Double | `0.0` | yes | command | controller |
| R1c_Joi5 | `ns=21;s=R1c_Joi5;` | Double | `0.0` | yes | command | controller |
| R1c_Joi6 | `ns=21;s=R1c_Joi6;` | Double | `0.0` | yes | command | controller |
| R1c_Joi7 | `ns=21;s=R1c_Joi7;` | Double | `0.0` | yes | command | controller |
| R1c_Vel | `ns=21;s=R1c_Vel;` | Double | `0.2` | yes | command | controller |
| R1c_PosX | `ns=21;s=R1c_PosX;` | Double | `0.0` | yes | command | controller |
| R1c_PosY | `ns=21;s=R1c_PosY;` | Double | `0.0` | yes | command | controller |
| R1c_PosZ | `ns=21;s=R1c_PosZ;` | Double | `0.0` | yes | command | controller |
| R1c_RotA | `ns=21;s=R1c_RotA;` | Double | `0.0` | yes | command | controller |
| R1c_RotB | `ns=21;s=R1c_RotB;` | Double | `0.0` | yes | command | controller |
| R1c_RotC | `ns=21;s=R1c_RotC;` | Double | `0.0` | yes | command | controller |
| R1c_int1 | `ns=21;s=R1c_int1;` | Int32 | `0` | yes | command | controller |
| R1c_int2 | `ns=21;s=R1c_int2;` | Int32 | `0` | yes | command | controller |
| R1c_int3 | `ns=21;s=R1c_int3;` | Int32 | `0` | yes | command | controller |
| R1c_GripperControl | `ns=21;s=R1c_GripperControl;` | Boolean | false | yes | command | controller |
| R1c_GripperAct | `ns=21;s=R1c_GripperAct;` | Boolean | false | yes | command | controller |
| R1c_GripperSpeed | `ns=21;s=R1c_GripperSpeed;` | Int32 | `0` | yes | command | controller |
| R1c_GripperForce | `ns=21;s=R1c_GripperForce;` | Int32 | `0` | yes | command | controller |
| R1c_GripperPos | `ns=21;s=R1c_GripperPos;` | Int32 | `0` | yes | command | controller |
| R1d_GripperAct | `ns=21;s=R1d_GripperAct;` | Boolean | false | yes | telemetry | device |
| R1d_GripperSpeed | `ns=21;s=R1d_GripperSpeed;` | Int32 | `0` | yes | telemetry | device |
| R1d_GripperForce | `ns=21;s=R1d_GripperForce;` | Int32 | `0` | yes | telemetry | device |
| R1d_GripperPos | `ns=21;s=R1d_GripperPos;` | Int32 | `0` | yes | telemetry | device |

### robot2

Object NodeId `ns=22;i=1`, namespace `22`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| R2d_Joi1 | `ns=22;s=R2d_Joi1;` | Double | `-15` | yes | telemetry | device |
| R2d_Joi2 | `ns=22;s=R2d_Joi2;` | Double | `39.0` | yes | telemetry | device |
| R2d_Joi3 | `ns=22;s=R2d_Joi3;` | Double | `1.0` | yes | telemetry | device |
| R2d_Joi4 | `ns=22;s=R2d_Joi4;` | Double | `-108.0` | yes | telemetry | device |
| R2d_Joi5 | `ns=22;s=R2d_Joi5;` | Double | `164.0` | yes | telemetry | device |
| R2d_Joi6 | `ns=22;s=R2d_Joi6;` | Double | `58.0` | yes | telemetry | device |
| R2d_Joi7 | `ns=22;s=R2d_Joi7;` | Double | `-82.0` | yes | telemetry | device |
| R2d_Tor1 | `ns=22;s=R2d_Tor1;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor2 | `ns=22;s=R2d_Tor2;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor3 | `ns=22;s=R2d_Tor3;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor4 | `ns=22;s=R2d_Tor4;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor5 | `ns=22;s=R2d_Tor5;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor6 | `ns=22;s=R2d_Tor6;` | Double | `0.0` | yes | telemetry | device |
| R2d_Tor7 | `ns=22;s=R2d_Tor7;` | Double | `0.0` | yes | telemetry | device |
| R2d_PosX | `ns=22;s=R2d_PosX;` | Double | `0.0` | yes | telemetry | device |
| R2d_PosY | `ns=22;s=R2d_PosY;` | Double | `0.0` | yes | telemetry | device |
| R2d_PosZ | `ns=22;s=R2d_PosZ;` | Double | `0.0` | yes | telemetry | device |
| R2d_RotA | `ns=22;s=R2d_RotA;` | Double | `0.0` | yes | telemetry | device |
| R2d_RotB | `ns=22;s=R2d_RotB;` | Double | `0.0` | yes | telemetry | device |
| R2d_RotC | `ns=22;s=R2d_RotC;` | Double | `0.0` | yes | telemetry | device |
| R2d_ForX | `ns=22;s=R2d_ForX;` | Double | `0.0` | yes | telemetry | device |
| R2d_ForY | `ns=22;s=R2d_ForY;` | Double | `0.0` | yes | telemetry | device |
| R2d_ForZ | `ns=22;s=R2d_ForZ;` | Double | `0.0` | yes | telemetry | device |
| R2d_MomX | `ns=22;s=R2d_MomX;` | Double | `0.0` | yes | telemetry | device |
| R2d_MomY | `ns=22;s=R2d_MomY;` | Double | `0.0` | yes | telemetry | device |
| R2d_MomZ | `ns=22;s=R2d_MomZ;` | Double | `0.0` | yes | telemetry | device |
| R2d_BaseX | `ns=22;s=R2d_BaseX;` | Double | `14.0` | yes | telemetry | device |
| R2d_BaseY | `ns=22;s=R2d_BaseY;` | Double | `11.5` | yes | telemetry | device |
| R2d_BaseA | `ns=22;s=R2d_BaseA;` | Double | `180.0` | yes | telemetry | device |
| R2d_Disconnect | `ns=22;s=R2d_Disconnect;` | Boolean | false | yes | telemetry | device |
| R2c_Connected | `ns=22;s=R2c_Connected;` | Boolean | true | yes | status | device |
| R2c_Start | `ns=22;s=R2c_Start;` | Boolean | false | yes | command | controller |
| R2c_ProgID | `ns=22;s=R2c_ProgID;` | Int32 | `0` | yes | command | controller |
| R2f_End | `ns=22;s=R2f_End;` | Boolean | false | yes | feedback | device |
| R2f_Ready | `ns=22;s=R2f_Ready;` | Boolean | false | yes | feedback | device |
| R2c_Joi1 | `ns=22;s=R2c_Joi1;` | Double | `0.0` | yes | command | controller |
| R2c_Joi2 | `ns=22;s=R2c_Joi2;` | Double | `0.0` | yes | command | controller |
| R2c_Joi3 | `ns=22;s=R2c_Joi3;` | Double | `0.0` | yes | command | controller |
| R2c_Joi4 | `ns=22;s=R2c_Joi4;` | Double | `0.0` | yes | command | controller |
| R2c_Joi5 | `ns=22;s=R2c_Joi5;` | Double | `0.0` | yes | command | controller |
| R2c_Joi6 | `ns=22;s=R2c_Joi6;` | Double | `0.0` | yes | command | controller |
| R2c_Joi7 | `ns=22;s=R2c_Joi7;` | Double | `0.0` | yes | command | controller |
| R2c_Vel | `ns=22;s=R2c_Vel;` | Double | `0.2` | yes | command | controller |
| R2c_PosX | `ns=22;s=R2c_PosX;` | Double | `0.0` | yes | command | controller |
| R2c_PosY | `ns=22;s=R2c_PosY;` | Double | `0.0` | yes | command | controller |
| R2c_PosZ | `ns=22;s=R2c_PosZ;` | Double | `0.0` | yes | command | controller |
| R2c_RotA | `ns=22;s=R2c_RotA;` | Double | `0.0` | yes | command | controller |
| R2c_RotB | `ns=22;s=R2c_RotB;` | Double | `0.0` | yes | command | controller |
| R2c_RotC | `ns=22;s=R2c_RotC;` | Double | `0.0` | yes | command | controller |
| R2c_int1 | `ns=22;s=R2c_int1;` | Int32 | `0` | yes | command | controller |
| R2c_int2 | `ns=22;s=R2c_int2;` | Int32 | `0` | yes | command | controller |
| R2c_int3 | `ns=22;s=R2c_int3;` | Int32 | `0` | yes | command | controller |
| R2c_GripperControl | `ns=22;s=R2c_GripperControl;` | Boolean | false | yes | command | controller |
| R2c_GripperAct | `ns=22;s=R2c_GripperAct;` | Boolean | false | yes | command | controller |
| R2c_GripperSpeed | `ns=22;s=R2c_GripperSpeed;` | Int32 | `0` | yes | command | controller |
| R2c_GripperForce | `ns=22;s=R2c_GripperForce;` | Int32 | `0` | yes | command | controller |
| R2c_GripperPos | `ns=22;s=R2c_GripperPos;` | Int32 | `0` | yes | command | controller |
| R2d_GripperAct | `ns=22;s=R2d_GripperAct;` | Boolean | false | yes | telemetry | device |
| R2d_GripperSpeed | `ns=22;s=R2d_GripperSpeed;` | Int32 | `0` | yes | telemetry | device |
| R2d_GripperForce | `ns=22;s=R2d_GripperForce;` | Int32 | `0` | yes | telemetry | device |
| R2d_GripperPos | `ns=22;s=R2d_GripperPos;` | Int32 | `0` | yes | telemetry | device |
| R2c_int4 | `ns=22;s=R2c_int4;` | Int32 | `0` | no | command | controller |
| R2c_int5 | `ns=22;s=R2c_int5;` | Int32 | `0` | no | command | controller |
| R2c_int6 | `ns=22;s=R2c_int6;` | Int32 | `0` | no | command | controller |
| R2c_Bool1 | `ns=22;s=R2c_Bool1;` | Boolean | false | no | command | controller |
| R2c_Bool2 | `ns=22;s=R2c_Bool2;` | Boolean | false | no | command | controller |
| R2c_Bool3 | `ns=22;s=R2c_Bool3;` | Boolean | false | no | command | controller |

### robot3

Object NodeId `ns=23;i=1`, namespace `23`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| R3d_Joi1 | `ns=23;s=R3d_Joi1;` | Double | `-15.0` | yes | telemetry | device |
| R3d_Joi2 | `ns=23;s=R3d_Joi2;` | Double | `39.0` | yes | telemetry | device |
| R3d_Joi3 | `ns=23;s=R3d_Joi3;` | Double | `1.0` | yes | telemetry | device |
| R3d_Joi4 | `ns=23;s=R3d_Joi4;` | Double | `-108.0` | yes | telemetry | device |
| R3d_Joi5 | `ns=23;s=R3d_Joi5;` | Double | `164.0` | yes | telemetry | device |
| R3d_Joi6 | `ns=23;s=R3d_Joi6;` | Double | `58.0` | yes | telemetry | device |
| R3d_Joi7 | `ns=23;s=R3d_Joi7;` | Double | `-82.0` | yes | telemetry | device |
| R3d_Tor1 | `ns=23;s=R3d_Tor1;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor2 | `ns=23;s=R3d_Tor2;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor3 | `ns=23;s=R3d_Tor3;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor4 | `ns=23;s=R3d_Tor4;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor5 | `ns=23;s=R3d_Tor5;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor6 | `ns=23;s=R3d_Tor6;` | Double | `0.0` | yes | telemetry | device |
| R3d_Tor7 | `ns=23;s=R3d_Tor7;` | Double | `0.0` | yes | telemetry | device |
| R3d_PosX | `ns=23;s=R3d_PosX;` | Double | `0.0` | yes | telemetry | device |
| R3d_PosY | `ns=23;s=R3d_PosY;` | Double | `0.0` | yes | telemetry | device |
| R3d_PosZ | `ns=23;s=R3d_PosZ;` | Double | `0.0` | yes | telemetry | device |
| R3d_RotA | `ns=23;s=R3d_RotA;` | Double | `0.0` | yes | telemetry | device |
| R3d_RotB | `ns=23;s=R3d_RotB;` | Double | `0.0` | yes | telemetry | device |
| R3d_RotC | `ns=23;s=R3d_RotC;` | Double | `0.0` | yes | telemetry | device |
| R3d_ForX | `ns=23;s=R3d_ForX;` | Double | `1.0` | yes | telemetry | device |
| R3d_ForY | `ns=23;s=R3d_ForY;` | Double | `1.0` | yes | telemetry | device |
| R3d_ForZ | `ns=23;s=R3d_ForZ;` | Double | `1.0` | yes | telemetry | device |
| R3d_MomX | `ns=23;s=R3d_MomX;` | Double | `0.0` | yes | telemetry | device |
| R3d_MomY | `ns=23;s=R3d_MomY;` | Double | `0.0` | yes | telemetry | device |
| R3d_MomZ | `ns=23;s=R3d_MomZ;` | Double | `0.0` | yes | telemetry | device |
| R3d_BaseX | `ns=23;s=R3d_BaseX;` | Double | `1.6` | yes | telemetry | device |
| R3d_BaseY | `ns=23;s=R3d_BaseY;` | Double | `3.45` | yes | telemetry | device |
| R3d_BaseA | `ns=23;s=R3d_BaseA;` | Int64 | `0` | yes | telemetry | device |
| R3d_Disconnect | `ns=23;s=R3d_Disconnect;` | Boolean | false | yes | telemetry | device |
| R3c_Connected | `ns=23;s=R3c_Connected;` | Boolean | true | yes | status | device |
| R3c_Start | `ns=23;s=R3c_Start;` | Boolean | false | yes | command | controller |
| R3c_ProgID | `ns=23;s=R3c_ProgID;` | Int32 | `0` | yes | command | controller |
| R3f_End | `ns=23;s=R3f_End;` | Boolean | false | yes | feedback | device |
| R3f_Ready | `ns=23;s=R3f_Ready;` | Boolean | false | yes | feedback | device |
| R3c_Joi1 | `ns=23;s=R3c_Joi1;` | Double | `0.0` | yes | command | controller |
| R3c_Joi2 | `ns=23;s=R3c_Joi2;` | Double | `0.0` | yes | command | controller |
| R3c_Joi3 | `ns=23;s=R3c_Joi3;` | Double | `0.0` | yes | command | controller |
| R3c_Joi4 | `ns=23;s=R3c_Joi4;` | Double | `0.0` | yes | command | controller |
| R3c_Joi5 | `ns=23;s=R3c_Joi5;` | Double | `0.0` | yes | command | controller |
| R3c_Joi6 | `ns=23;s=R3c_Joi6;` | Double | `0.0` | yes | command | controller |
| R3c_Joi7 | `ns=23;s=R3c_Joi7;` | Double | `0.0` | yes | command | controller |
| R3c_Vel | `ns=23;s=R3c_Vel;` | Double | `0.2` | yes | command | controller |
| R3c_PosX | `ns=23;s=R3c_PosX;` | Double | `0.0` | yes | command | controller |
| R3c_PosY | `ns=23;s=R3c_PosY;` | Double | `0.0` | yes | command | controller |
| R3c_PosZ | `ns=23;s=R3c_PosZ;` | Double | `0.0` | yes | command | controller |
| R3c_RotA | `ns=23;s=R3c_RotA;` | Double | `0.0` | yes | command | controller |
| R3c_RotB | `ns=23;s=R3c_RotB;` | Double | `0.0` | yes | command | controller |
| R3c_RotC | `ns=23;s=R3c_RotC;` | Double | `0.0` | yes | command | controller |
| R3c_int1 | `ns=23;s=R3c_int1;` | Int32 | `0` | yes | command | controller |
| R3c_int2 | `ns=23;s=R3c_int2;` | Int32 | `0` | yes | command | controller |
| R3c_int3 | `ns=23;s=R3c_int3;` | Int32 | `0` | yes | command | controller |
| R3c_GripperControl | `ns=23;s=R3c_GripperControl;` | Boolean | false | yes | command | controller |
| R3c_GripperAct | `ns=23;s=R3c_GripperAct;` | Boolean | false | yes | command | controller |
| R3c_GripperSpeed | `ns=23;s=R3c_GripperSpeed;` | Int32 | `0` | yes | command | controller |
| R3c_GripperForce | `ns=23;s=R3c_GripperForce;` | Int32 | `0` | yes | command | controller |
| R3c_GripperPos | `ns=23;s=R3c_GripperPos;` | Int32 | `0` | yes | command | controller |
| R3d_GripperAct | `ns=23;s=R3d_GripperAct;` | Boolean | false | yes | telemetry | device |
| R3d_GripperSpeed | `ns=23;s=R3d_GripperSpeed;` | Int32 | `0` | yes | telemetry | device |
| R3d_GripperForce | `ns=23;s=R3d_GripperForce;` | Int32 | `0` | yes | telemetry | device |
| R3d_GripperPos | `ns=23;s=R3d_GripperPos;` | Int32 | `0` | yes | telemetry | device |
| R3d_GripperStatus | `ns=23;s=R3d_GripperStatus;` | Int32 | `0` | yes | telemetry | device |

### robot4

Object NodeId `ns=24;i=1`, namespace `24`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| R4d_Joi1 | `ns=24;s=R4d_Joi1;` | Double | `-15.0` | yes | telemetry | device |
| R4d_Joi2 | `ns=24;s=R4d_Joi2;` | Double | `39.0` | yes | telemetry | device |
| R4d_Joi3 | `ns=24;s=R4d_Joi3;` | Double | `1.0` | yes | telemetry | device |
| R4d_Joi4 | `ns=24;s=R4d_Joi4;` | Double | `-108.0` | yes | telemetry | device |
| R4d_Joi5 | `ns=24;s=R4d_Joi5;` | Double | `164.0` | yes | telemetry | device |
| R4d_Joi6 | `ns=24;s=R4d_Joi6;` | Double | `58.0` | yes | telemetry | device |
| R4d_Joi7 | `ns=24;s=R4d_Joi7;` | Double | `-82.0` | yes | telemetry | device |
| R4d_Tor1 | `ns=24;s=R4d_Tor1;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor2 | `ns=24;s=R4d_Tor2;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor3 | `ns=24;s=R4d_Tor3;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor4 | `ns=24;s=R4d_Tor4;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor5 | `ns=24;s=R4d_Tor5;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor6 | `ns=24;s=R4d_Tor6;` | Double | `0.0` | yes | telemetry | device |
| R4d_Tor7 | `ns=24;s=R4d_Tor7;` | Double | `0.0` | yes | telemetry | device |
| R4d_PosX | `ns=24;s=R4d_PosX;` | Double | `0.0` | yes | telemetry | device |
| R4d_PosY | `ns=24;s=R4d_PosY;` | Double | `0.0` | yes | telemetry | device |
| R4d_PosZ | `ns=24;s=R4d_PosZ;` | Double | `0.0` | yes | telemetry | device |
| R4d_RotA | `ns=24;s=R4d_RotA;` | Double | `0.0` | yes | telemetry | device |
| R4d_RotB | `ns=24;s=R4d_RotB;` | Double | `0.0` | yes | telemetry | device |
| R4d_RotC | `ns=24;s=R4d_RotC;` | Double | `0.0` | yes | telemetry | device |
| R4d_ForX | `ns=24;s=R4d_ForX;` | Double | `0.0` | yes | telemetry | device |
| R4d_ForY | `ns=24;s=R4d_ForY;` | Double | `0.0` | yes | telemetry | device |
| R4d_ForZ | `ns=24;s=R4d_ForZ;` | Double | `0.0` | yes | telemetry | device |
| R4d_MomX | `ns=24;s=R4d_MomX;` | Double | `0.0` | yes | telemetry | device |
| R4d_MomY | `ns=24;s=R4d_MomY;` | Double | `0.0` | yes | telemetry | device |
| R4d_MomZ | `ns=24;s=R4d_MomZ;` | Double | `0.0` | yes | telemetry | device |
| R4d_BaseX | `ns=24;s=R4d_BaseX;` | Double | `12.8` | yes | telemetry | device |
| R4d_BaseY | `ns=24;s=R4d_BaseY;` | Double | `0.5` | yes | telemetry | device |
| R4d_BaseA | `ns=24;s=R4d_BaseA;` | Double | `180.0` | yes | telemetry | device |
| R4d_Disconnect | `ns=24;s=R4d_Disconnect;` | Boolean | false | yes | telemetry | device |
| R4c_Connected | `ns=24;s=R4c_Connected;` | Boolean | true | yes | status | device |
| R4c_Start | `ns=24;s=R4c_Start;` | Boolean | false | yes | command | controller |
| R4c_ProgID | `ns=24;s=R4c_ProgID;` | Int32 | `0` | yes | command | controller |
| R4f_End | `ns=24;s=R4f_End;` | Boolean | false | yes | feedback | device |
| R4f_Ready | `ns=24;s=R4f_Ready;` | Boolean | false | yes | feedback | device |
| R4c_Joi1 | `ns=24;s=R4c_Joi1;` | Double | `0.0` | yes | command | controller |
| R4c_Joi2 | `ns=24;s=R4c_Joi2;` | Double | `0.0` | yes | command | controller |
| R4c_Joi3 | `ns=24;s=R4c_Joi3;` | Double | `0.0` | yes | command | controller |
| R4c_Joi4 | `ns=24;s=R4c_Joi4;` | Double | `0.0` | yes | command | controller |
| R4c_Joi5 | `ns=24;s=R4c_Joi5;` | Double | `0.0` | yes | command | controller |
| R4c_Joi6 | `ns=24;s=R4c_Joi6;` | Double | `0.0` | yes | command | controller |
| R4c_Joi7 | `ns=24;s=R4c_Joi7;` | Double | `0.0` | yes | command | controller |
| R4c_Vel | `ns=24;s=R4c_Vel;` | Double | `0.2` | yes | command | controller |
| R4c_PosX | `ns=24;s=R4c_PosX;` | Double | `0.0` | yes | command | controller |
| R4c_PosY | `ns=24;s=R4c_PosY;` | Double | `0.0` | yes | command | controller |
| R4c_PosZ | `ns=24;s=R4c_PosZ;` | Double | `0.0` | yes | command | controller |
| R4c_RotA | `ns=24;s=R4c_RotA;` | Double | `0.0` | yes | command | controller |
| R4c_RotB | `ns=24;s=R4c_RotB;` | Double | `0.0` | yes | command | controller |
| R4c_RotC | `ns=24;s=R4c_RotC;` | Double | `0.0` | yes | command | controller |
| R4c_int1 | `ns=24;s=R4c_int1;` | Int32 | `0` | yes | command | controller |
| R4c_int2 | `ns=24;s=R4c_int2;` | Int32 | `0` | yes | command | controller |
| R4c_int3 | `ns=24;s=R4c_int3;` | Int32 | `0` | yes | command | controller |
| R4c_err | `ns=24;s=R4c_err;` | String | `A` | yes | status | device |
| R4c_sev | `ns=24;s=R4c_sev;` | Int32 | `0` | yes | status | device |
| R4c_GripperControl | `ns=24;s=R4c_GripperControl;` | Boolean | false | yes | command | controller |
| R4c_GripperAct | `ns=24;s=R4c_GripperAct;` | Boolean | false | yes | command | controller |
| R4c_GripperSpeed | `ns=24;s=R4c_GripperSpeed;` | Int32 | `0` | yes | command | controller |
| R4c_GripperForce | `ns=24;s=R4c_GripperForce;` | Int32 | `0` | yes | command | controller |
| R4c_GripperPos | `ns=24;s=R4c_GripperPos;` | Int32 | `0` | yes | command | controller |
| R4d_GripperAct | `ns=24;s=R4d_GripperAct;` | Boolean | false | yes | telemetry | device |
| R4d_GripperSpeed | `ns=24;s=R4d_GripperSpeed;` | Int32 | `0` | yes | telemetry | device |
| R4d_GripperForce | `ns=24;s=R4d_GripperForce;` | Int32 | `0` | yes | telemetry | device |
| R4d_GripperPos | `ns=24;s=R4d_GripperPos;` | Int32 | `0` | yes | telemetry | device |

### Printer1

Object NodeId `ns=11;i=1`, namespace `11`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| P1c_ProgID | `ns=11;s=P1c_ProgID;` | Int32 | `0` | yes | command | controller |
| P1c_Start | `ns=11;s=P1c_Start;` | Boolean | false | yes | command | controller |
| P1f_Ready | `ns=11;s=P1f_Ready;` | Boolean | false | yes | feedback | device |
| P1f_End | `ns=11;s=P1f_End;` | Boolean | false | yes | feedback | device |
| P1c_PartRemoved | `ns=11;s=P1c_PartRemoved;` | Boolean | false | yes | command | controller |
| P1c_BedCleaned | `ns=11;s=P1c_BedCleaned;` | Boolean | false | yes | command | controller |
| P1c_File | `ns=11;s=P1c_File;` | String | `Default` | yes | command | controller |
| P1c_JogX | `ns=11;s=P1c_JogX;` | Double | `0.0` | yes | command | controller |
| P1c_JogY | `ns=11;s=P1c_JogY;` | Double | `0.0` | yes | command | controller |
| P1c_JogZ | `ns=11;s=P1c_JogZ;` | Double | `0.0` | yes | command | controller |
| P1c_JogSpeed | `ns=11;s=P1c_JogSpeed;` | Double | `0.0` | yes | command | controller |
| P1c_Feedrate | `ns=11;s=P1c_Feedrate;` | Double | `0.0` | yes | command | controller |
| P1c_tNozTarget | `ns=11;s=P1c_tNozTarget;` | Double | `0.0` | yes | command | controller |
| P1c_tNozOffset | `ns=11;s=P1c_tNozOffset;` | Double | `0.0` | yes | command | controller |
| P1c_tBedTarget | `ns=11;s=P1c_tBedTarget;` | Double | `0.0` | yes | command | controller |
| P1c_tBedOffset | `ns=11;s=P1c_tBedOffset;` | Double | `0.0` | yes | command | controller |
| P1c_Extrude | `ns=11;s=P1c_Extrude;` | Double | `0.0` | yes | command | controller |
| P1d_State | `ns=11;s=P1d_State;` | String | `Default` | yes | telemetry | device |
| P1d_APIresp | `ns=11;s=P1d_APIresp` | String | `Default` | yes | telemetry | device |
| P1d_tNozTarget | `ns=11;s=P1d_tNozTarget;` | Double | `0.0` | yes | telemetry | device |
| P1d_tNozReal | `ns=11;s=P1d_tNozReal;` | Double | `0.0` | yes | telemetry | device |
| P1d_tBedTarget | `ns=11;s=P1d_tBedTarget;` | Double | `0.0` | yes | telemetry | device |
| P1d_tBedReal | `ns=11;s=P1d_tBedReal;` | Double | `0.0` | yes | telemetry | device |
| P1d_JobTimeEst | `ns=11;s=P1d_JobTimeEst;` | Double | `0.0` | yes | telemetry | device |
| P1d_FilaLenEst | `ns=11;s=P1d_FilaLenEst;` | Double | `0.0` | yes | telemetry | device |
| P1d_JobFile | `ns=11;s=P1d_JobFile;` | String | `Default` | yes | telemetry | device |
| P1d_JobProgress | `ns=11;s=P1d_JobProgress;` | Double | `0.0` | yes | telemetry | device |
| P1d_JobTime | `ns=11;s=P1d_JobTime;` | Double | `0.0` | yes | telemetry | device |
| P1d_JobTimeLeft | `ns=11;s=P1d_JobTimeLeft;` | Double | `0.0` | yes | telemetry | device |
| P1d_Message | `ns=11;s=P1d_Message` | String | `Default` | yes | telemetry | device |

### Printer2

Object NodeId `ns=12;i=1`, namespace `12`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| P2c_ProgID | `ns=12;s=P2c_ProgID;` | Int32 | `0` | yes | command | controller |
| P2c_Start | `ns=12;s=P2c_Start;` | Boolean | false | yes | command | controller |
| P2f_Ready | `ns=12;s=P2f_Ready;` | Boolean | false | yes | feedback | device |
| P2f_End | `ns=12;s=P2f_End;` | Boolean | false | yes | feedback | device |
| P2c_PartRemoved | `ns=12;s=P2c_PartRemoved;` | Boolean | false | yes | command | controller |
| P2c_BedCleaned | `ns=12;s=P2c_BedCleaned;` | Boolean | false | yes | command | controller |
| P2c_File | `ns=12;s=P2c_File;` | String | `Default` | yes | command | controller |
| P2c_JogX | `ns=12;s=P2c_JogX;` | Double | `0.0` | yes | command | controller |
| P2c_JogY | `ns=12;s=P2c_JogY;` | Double | `0.0` | yes | command | controller |
| P2c_JogZ | `ns=12;s=P2c_JogZ;` | Double | `0.0` | yes | command | controller |
| P2c_JogSpeed | `ns=12;s=P2c_JogSpeed;` | Double | `0.0` | yes | command | controller |
| P2c_Feedrate | `ns=12;s=P2c_Feedrate;` | Double | `0.0` | yes | command | controller |
| P2c_tNozTarget | `ns=12;s=P2c_tNozTarget;` | Double | `0.0` | yes | command | controller |
| P2c_tNozOffset | `ns=12;s=P2c_tNozOffset;` | Double | `0.0` | yes | command | controller |
| P2c_tBedTarget | `ns=12;s=P2c_tBedTarget;` | Double | `0.0` | yes | command | controller |
| P2c_tBedOffset | `ns=12;s=P2c_tBedOffset;` | Double | `0.0` | yes | command | controller |
| P2c_Extrude | `ns=12;s=P2c_Extrude;` | Double | `0.0` | yes | command | controller |
| P2d_State | `ns=12;s=P2d_State;` | String | `Default` | yes | telemetry | device |
| P2d_APIresp | `ns=12;s=P2d_APIresp` | String | `Default` | yes | telemetry | device |
| P2d_tNozTarget | `ns=12;s=P2d_tNozTarget;` | Double | `0.0` | yes | telemetry | device |
| P2d_tNozReal | `ns=12;s=P2d_tNozReal;` | Double | `0.0` | yes | telemetry | device |
| P2d_tBedTarget | `ns=12;s=P2d_tBedTarget;` | Double | `0.0` | yes | telemetry | device |
| P2d_tBedReal | `ns=12;s=P2d_tBedReal;` | Double | `0.0` | yes | telemetry | device |
| P2d_JobTimeEst | `ns=12;s=P2d_JobTimeEst;` | Double | `0.0` | yes | telemetry | device |
| P2d_FilaLenEst | `ns=12;s=P2d_FilaLenEst;` | Double | `0.0` | yes | telemetry | device |
| P2d_JobFile | `ns=12;s=P2d_JobFile;` | String | `Default` | yes | telemetry | device |
| P2d_JobProgress | `ns=12;s=P2d_JobProgress;` | Double | `0.0` | yes | telemetry | device |
| P2d_JobTime | `ns=12;s=P2d_JobTime;` | Double | `0.0` | yes | telemetry | device |
| P2d_JobTimeLeft | `ns=12;s=P2d_JobTimeLeft;` | Double | `0.0` | yes | telemetry | device |
| P2d_Message | `ns=12;s=P2d_Message` | String | `Default` | yes | telemetry | device |

### Printer3

Object NodeId `ns=13;i=1`, namespace `13`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| P3c_ProgID | `ns=13;s=P3c_ProgID;` | Int32 | `0` | yes | command | controller |
| P3c_Start | `ns=13;s=P3c_Start;` | Boolean | false | yes | command | controller |
| P3f_Ready | `ns=13;s=P3f_Ready;` | Boolean | false | yes | feedback | device |
| P3f_End | `ns=13;s=P3f_End;` | Boolean | false | yes | feedback | device |
| P3c_PartRemoved | `ns=13;s=P3c_PartRemoved;` | Boolean | false | yes | command | controller |
| P3c_BedCleaned | `ns=13;s=P3c_BedCleaned;` | Boolean | false | yes | command | controller |
| P3c_File | `ns=13;s=P3c_File;` | String | `Default` | yes | command | controller |
| P3c_JogX | `ns=13;s=P3c_JogX;` | Double | `0.0` | yes | command | controller |
| P3c_JogY | `ns=13;s=P3c_JogY;` | Double | `0.0` | yes | command | controller |
| P3c_JogZ | `ns=13;s=P3c_JogZ;` | Double | `0.0` | yes | command | controller |
| P3c_JogSpeed | `ns=13;s=P3c_JogSpeed;` | Double | `0.0` | yes | command | controller |
| P3c_Feedrate | `ns=13;s=P3c_Feedrate;` | Double | `0.0` | yes | command | controller |
| P3c_tNozTarget | `ns=13;s=P3c_tNozTarget;` | Double | `0.0` | yes | command | controller |
| P3c_tNozOffset | `ns=13;s=P3c_tNozOffset;` | Double | `0.0` | yes | command | controller |
| P3c_tBedTarget | `ns=13;s=P3c_tBedTarget;` | Double | `0.0` | yes | command | controller |
| P3c_tBedOffset | `ns=13;s=P3c_tBedOffset;` | Double | `0.0` | yes | command | controller |
| P3c_Extrude | `ns=13;s=P3c_Extrude;` | Double | `0.0` | yes | command | controller |
| P3d_State | `ns=13;s=P3d_State;` | String | `Default` | yes | telemetry | device |
| P3d_APIresp | `ns=13;s=P3d_APIresp` | String | `Default` | yes | telemetry | device |
| P3d_tNozTarget | `ns=13;s=P3d_tNozTarget;` | Double | `0.0` | yes | telemetry | device |
| P3d_tNozReal | `ns=13;s=P3d_tNozReal;` | Double | `0.0` | yes | telemetry | device |
| P3d_tBedTarget | `ns=13;s=P3d_tBedTarget;` | Double | `0.0` | yes | telemetry | device |
| P3d_tBedReal | `ns=13;s=P3d_tBedReal;` | Double | `0.0` | yes | telemetry | device |
| P3d_JobTimeEst | `ns=13;s=P3d_JobTimeEst;` | Double | `0.0` | yes | telemetry | device |
| P3d_FilaLenEst | `ns=13;s=P3d_FilaLenEst;` | Double | `0.0` | yes | telemetry | device |
| P3d_JobFile | `ns=13;s=P3d_JobFile;` | String | `Default` | yes | telemetry | device |
| P3d_JobProgress | `ns=13;s=P3d_JobProgress;` | Double | `0.0` | yes | telemetry | device |
| P3d_JobTime | `ns=13;s=P3d_JobTime;` | Double | `0.0` | yes | telemetry | device |
| P3d_JobTimeLeft | `ns=13;s=P3d_JobTimeLeft;` | Double | `0.0` | yes | telemetry | device |
| P3d_Message | `ns=13;s=P3d_Message` | String | `Default` | yes | telemetry | device |

### Printer4

Object NodeId `ns=14;i=1`, namespace `14`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| P4c_ProgID | `ns=14;s=P4c_ProgID;` | Int32 | `0` | yes | command | controller |
| P4c_Start | `ns=14;s=P4c_Start;` | Boolean | false | yes | command | controller |
| P4f_Ready | `ns=14;s=P4f_Ready;` | Boolean | false | yes | feedback | device |
| P4f_End | `ns=14;s=P4f_End;` | Boolean | false | yes | feedback | device |
| P4c_PartRemoved | `ns=14;s=P4c_PartRemoved;` | Boolean | false | yes | command | controller |
| P4c_BedCleaned | `ns=14;s=P4c_BedCleaned;` | Boolean | false | yes | command | controller |
| P4c_File | `ns=14;s=P4c_File;` | String | `Default` | yes | command | controller |
| P4c_JogX | `ns=14;s=P4c_JogX;` | Double | `0.0` | yes | command | controller |
| P4c_JogY | `ns=14;s=P4c_JogY;` | Double | `0.0` | yes | command | controller |
| P4c_JogZ | `ns=14;s=P4c_JogZ;` | Double | `0.0` | yes | command | controller |
| P4c_JogSpeed | `ns=14;s=P4c_JogSpeed;` | Double | `0.0` | yes | command | controller |
| P4c_Feedrate | `ns=14;s=P4c_Feedrate;` | Double | `0.0` | yes | command | controller |
| P4c_tNozTarget | `ns=14;s=P4c_tNozTarget;` | Double | `0.0` | yes | command | controller |
| P4c_tNozOffset | `ns=14;s=P4c_tNozOffset;` | Double | `0.0` | yes | command | controller |
| P4c_tBedTarget | `ns=14;s=P4c_tBedTarget;` | Double | `0.0` | yes | command | controller |
| P4c_tBedOffset | `ns=14;s=P4c_tBedOffset;` | Double | `0.0` | yes | command | controller |
| P4c_Extrude | `ns=14;s=P4c_Extrude;` | Double | `0.0` | yes | command | controller |
| P4d_State | `ns=14;s=P4d_State;` | String | `Default` | yes | telemetry | device |
| P4d_APIresp | `ns=14;s=P4d_APIresp` | String | `Default` | yes | telemetry | device |
| P4d_tNozTarget | `ns=14;s=P4d_tNozTarget;` | Double | `0.0` | yes | telemetry | device |
| P4d_tNozReal | `ns=14;s=P4d_tNozReal;` | Double | `0.0` | yes | telemetry | device |
| P4d_tBedTarget | `ns=14;s=P4d_tBedTarget;` | Double | `0.0` | yes | telemetry | device |
| P4d_tBedReal | `ns=14;s=P4d_tBedReal;` | Double | `0.0` | yes | telemetry | device |
| P4d_JobTimeEst | `ns=14;s=P4d_JobTimeEst;` | Double | `0.0` | yes | telemetry | device |
| P4d_FilaLenEst | `ns=14;s=P4d_FilaLenEst;` | Double | `0.0` | yes | telemetry | device |
| P4d_JobFile | `ns=14;s=P4d_JobFile;` | String | `Default` | yes | telemetry | device |
| P4d_JobProgress | `ns=14;s=P4d_JobProgress;` | Double | `0.0` | yes | telemetry | device |
| P4d_JobTime | `ns=14;s=P4d_JobTime;` | Double | `0.0` | yes | telemetry | device |
| P4d_JobTimeLeft | `ns=14;s=P4d_JobTimeLeft;` | Double | `0.0` | yes | telemetry | device |
| P4d_Message | `ns=14;s=P4d_Message` | String | `Default` | yes | telemetry | device |

### Camera1

Object NodeId `ns=31;i=1`, namespace `31`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| C1c_Snap | `ns=31;s=C1c_Snap;` | Boolean | false | yes | command | controller |
| C1c_Rec | `ns=31;s=C1c_Rec;` | Boolean | false | yes | command | controller |
| C1c_Name | `ns=31;s=C1c_Name;` | String | `Default` | yes | command | controller |
| C1f_Ready | `ns=31;s=C1f_Ready;` | Boolean | false | yes | feedback | device |
| C1f_End | `ns=31;s=C1f_End;` | Boolean | false | yes | feedback | device |
| C1d_Img | `ns=31;s=C1d_Img;` | ByteString | `00000000` (4 bytes) | yes | telemetry | device |
| C1d_Img_h | `ns=31;s=C1d_Img_h;` | Int64 | `0` | yes | telemetry | device |
| C1d_Img_w | `ns=31;s=C1d_Img_w;` | Int64 | `0` | yes | telemetry | device |

### RobotDog1

Object NodeId `ns=29;i=1`, namespace `29`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| RD1d_FR0Angle | `ns=29;s=RD1d_FR0Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FR1Angle | `ns=29;s=RD1d_FR1Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FR2Angle | `ns=29;s=RD1d_FR2Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL0Angle | `ns=29;s=RD1d_FL0Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL1Angle | `ns=29;s=RD1d_FL1Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL2Angle | `ns=29;s=RD1d_FL2Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR0Angle | `ns=29;s=RD1d_BR0Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR1Angle | `ns=29;s=RD1d_BR1Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR2Angle | `ns=29;s=RD1d_BR2Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL0Angle | `ns=29;s=RD1d_BL0Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL1Angle | `ns=29;s=RD1d_BL1Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL2Angle | `ns=29;s=RD1d_BL2Angle;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FR0Temp | `ns=29;s=RD1d_FR0Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FR1Temp | `ns=29;s=RD1d_FR1Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FR2Temp | `ns=29;s=RD1d_FR2Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FL0Temp | `ns=29;s=RD1d_FL0Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FL1Temp | `ns=29;s=RD1d_FL1Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FL2Temp | `ns=29;s=RD1d_FL2Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BR0Temp | `ns=29;s=RD1d_BR0Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BR1Temp | `ns=29;s=RD1d_BR1Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BR2Temp | `ns=29;s=RD1d_BR2Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BL0Temp | `ns=29;s=RD1d_BL0Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BL1Temp | `ns=29;s=RD1d_BL1Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BL2Temp | `ns=29;s=RD1d_BL2Temp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FR0Tau | `ns=29;s=RD1d_FR0Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FR1Tau | `ns=29;s=RD1d_FR1Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FR2Tau | `ns=29;s=RD1d_FR2Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL0Tau | `ns=29;s=RD1d_FL0Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL1Tau | `ns=29;s=RD1d_FL1Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_FL2Tau | `ns=29;s=RD1d_FL2Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR0Tau | `ns=29;s=RD1d_BR0Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR1Tau | `ns=29;s=RD1d_BR1Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BR2Tau | `ns=29;s=RD1d_BR2Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL0Tau | `ns=29;s=RD1d_BL0Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL1Tau | `ns=29;s=RD1d_BL1Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_BL2Tau | `ns=29;s=RD1d_BL2Tau;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Charge | `ns=29;s=RD1d_Charge;` | Int32 | `0` | yes | telemetry | device |
| RD1d_QuadternionW | `ns=29;s=RD1d_QuadternionW;` | Double | `0.0` | yes | telemetry | device |
| RD1d_QuadternionX | `ns=29;s=RD1d_QuadternionX;` | Double | `0.0` | yes | telemetry | device |
| RD1d_QuadternionY | `ns=29;s=RD1d_QuadternionY;` | Double | `0.0` | yes | telemetry | device |
| RD1d_QuadternionZ | `ns=29;s=RD1d_QuadternionZ;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Gyro0 | `ns=29;s=RD1d_Gyro0;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Gyro1 | `ns=29;s=RD1d_Gyro1;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Gyro2 | `ns=29;s=RD1d_Gyro2;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Acc0 | `ns=29;s=RD1d_Acc0;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Acc1 | `ns=29;s=RD1d_Acc1;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Acc2 | `ns=29;s=RD1d_Acc2;` | Double | `0.0` | yes | telemetry | device |
| RD1d_rpy0 | `ns=29;s=RD1d_rpy0;` | Double | `0.0` | yes | telemetry | device |
| RD1d_rpy1 | `ns=29;s=RD1d_rpy1;` | Double | `0.0` | yes | telemetry | device |
| RD1d_rpy2 | `ns=29;s=RD1d_rpy2;` | Double | `0.0` | yes | telemetry | device |
| RD1d_IMUTemp | `ns=29;s=RD1d_IMUTemp;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FRFootForce | `ns=29;s=RD1d_FRFootForce;` | Int32 | `0` | yes | telemetry | device |
| RD1d_FLFootForce | `ns=29;s=RD1d_FLFootForce;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BRFootForce | `ns=29;s=RD1d_BRFootForce;` | Int32 | `0` | yes | telemetry | device |
| RD1d_BLFootForce | `ns=29;s=RD1d_BLFootForce;` | Int32 | `0` | yes | telemetry | device |
| RD1d_Pos0 | `ns=29;s=RD1d_Pos0;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Pos1 | `ns=29;s=RD1d_Pos1;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Pos2 | `ns=29;s=RD1d_Pos2;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Vel0 | `ns=29;s=RD1d_Vel0;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Vel1 | `ns=29;s=RD1d_Vel1;` | Double | `0.0` | yes | telemetry | device |
| RD1d_Vel2 | `ns=29;s=RD1d_Vel2;` | Double | `0.0` | yes | telemetry | device |
| RD1d_YawSpeed | `ns=29;s=RD1d_YawSpeed;` | Double | `0.0` | yes | telemetry | device |

### AirPurifier1

Object NodeId `ns=41;i=1`, namespace `41`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| AP1c_Name | `ns=41;s=AP1c_Name;` | String | `Perry the Air Purifier` | yes | command | controller |
| AP1c_PWR | `ns=41;s=AP1c_PWR;` | Boolean | true | yes | command | controller |
| AP1c_Mode | `ns=41;s=AP1c_Mode;` | Int32 | `0` | yes | command | controller |
| AP1c_CL | `ns=41;s=AP1c_CL;` | Boolean | false | yes | command | controller |
| AP1c_BtnLight | `ns=41;s=AP1c_BtnLight;` | Boolean | false | yes | command | controller |
| AP1c_DisplayIndex | `ns=41;s=AP1c_DisplayIndex;` | Boolean | true | yes | command | controller |
| AP1d_PM25 | `ns=41;s=AP1d_PM25;` | Int32 | `0` | yes | telemetry | device |
| AP1d_Allergens | `ns=41;s=AP1d_Allergens;` | Int32 | `0` | yes | telemetry | device |
| AP1d_FilterStatus0 | `ns=41;s=AP1d_FilterStatus0;` | Int32 | `0` | yes | telemetry | device |
| AP1d_FilterStatus1 | `ns=41;s=AP1d_FilterStatus1;` | Int32 | `0` | yes | telemetry | device |
| AP1d_FilterStatus2 | `ns=41;s=AP1d_FilterStatus2;` | Int32 | `0` | yes | telemetry | device |

### AirPurifier2

Object NodeId `ns=42;i=1`, namespace `42`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| AP2c_Name | `ns=42;s=AP2c_Name;` | String | `Kermit the Air Purifier` | yes | command | controller |
| AP2c_PWR | `ns=42;s=AP2c_PWR;` | Boolean | true | yes | command | controller |
| AP2c_Mode | `ns=42;s=AP2c_Mode;` | Int32 | `0` | yes | command | controller |
| AP2c_CL | `ns=42;s=AP2c_CL;` | Boolean | false | yes | command | controller |
| AP2c_BtnLight | `ns=42;s=AP2c_BtnLight;` | Boolean | false | yes | command | controller |
| AP2c_DisplayIndex | `ns=42;s=AP2c_DisplayIndex;` | Boolean | true | yes | command | controller |
| AP2d_PM25 | `ns=42;s=AP2d_PM25;` | Int32 | `0` | yes | telemetry | device |
| AP2d_Allergens | `ns=42;s=AP2d_Allergens;` | Int32 | `0` | yes | telemetry | device |
| AP2d_FilterStatus0 | `ns=42;s=AP2d_FilterStatus0;` | Int32 | `0` | yes | telemetry | device |
| AP2d_FilterStatus1 | `ns=42;s=AP2d_FilterStatus1;` | Int32 | `0` | yes | telemetry | device |
| AP2d_FilterStatus2 | `ns=42;s=AP2d_FilterStatus2;` | Int32 | `0` | yes | telemetry | device |

### Glove 1 (Left)

Object NodeId `ns=51;i=1`, namespace `51`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| Gd_VibrationIntensity | `ns=51;s=Gd_VibrationIntensity;` | Double | `0.0` | yes | telemetry | device |
| Gd_LockStatus | `ns=51;s=Gd_LockStatus;` | Boolean | false | yes | telemetry | device |
| Gd_GripperDistance | `ns=51;s=Gd_GripperDistance;` | Double | `0.0` | yes | telemetry | device |
| Gc_VibrationIntensity | `ns=51;s=Gc_VibrationIntensity;` | Double | `0.0` | yes | command | controller |
| Gc_LockStatus | `ns=51;s=Gc_LockStatus;` | Boolean | false | yes | command | controller |
| Gf_Connection | `ns=51;s=Gf_Connection;` | Boolean | false | yes | feedback | device |
| Gf_Ready | `ns=51;s=Gf_Ready;` | Boolean | false | yes | feedback | device |

### Glove 2 (Right)

Object NodeId `ns=52;i=1`, namespace `52`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| Gd_VibrationIntensity | `ns=52;s=Gd_VibrationIntensity;` | Double | `0.0` | yes | telemetry | device |
| Gd_LockStatus | `ns=52;s=Gd_LockStatus;` | Boolean | false | yes | telemetry | device |
| Gd_GripperDistance | `ns=52;s=Gd_GripperDistance;` | Double | `0.0` | yes | telemetry | device |
| Gc_VibrationIntensity | `ns=52;s=Gc_VibrationIntensity;` | Double | `0.0` | yes | command | controller |
| Gc_LockStatus | `ns=52;s=Gc_LockStatus;` | Boolean | false | yes | command | controller |
| Gf_Connection | `ns=52;s=Gf_Connection;` | Boolean | false | yes | feedback | device |
| Gf_Ready | `ns=52;s=Gf_Ready;` | Boolean | false | yes | feedback | device |

### 500 RGB LEDs

Object NodeId `ns=53;i=1`, namespace `53`.

| Browse name | NodeId | Data type | Default | Writable | Category | Writer |
|---|---|---|---|---|---|---|
| RGBf_Ready | `ns=53;s=RGBf_Ready;` | Boolean | false | yes | feedback | device |
| RGBf_Status | `ns=53;s=RGBf_Status;` | Boolean | false | yes | feedback | device |
| RGBc_Start | `ns=53;s=RGBc_Start;` | Boolean | false | yes | command | controller |
| RGBc_ProgID | `ns=53;s=RGBc_ProgID;` | Int64 | `0` | yes | command | controller |
| RGBc_Img | `ns=53;s=RGBc_Img;` | ByteString | `00000000` (4 bytes) | yes | command | controller |

## Permissions

Enforcement: disabled (legacy profile). A batched write containing any unauthorized NodeId is rejected as a whole.

| Role | Read | Writable owners |
|---|---|---|
| admin | yes | all writable variables |
| controller | yes | controller |
| device | yes | device |
| monitor | yes | none |

## Package modules

| Module | Responsibility |
|---|---|
| `__main__.py` | Command-line entry point. |
| `audit.py` | Command and security event auditing. |
| `docs.py` | Deterministic, self-documenting reference generator. |
| `equipment_registry.py` | Built equipment registry and NodeId ownership lookup. |
| `health.py` | Additive equipment health and stale-data detection (Phase 6). |
| `legacy_parser.py` | Static extraction of the frozen legacy interface. |
| `logging_config.py` | Structured logging setup. |
| `models.py` | Validated configuration and address-space models. |
| `namespaces.py` | Exact namespace construction. |
| `node_factory.py` | Typed address-space creation from validated configuration. |
| `permissions.py` | Production authorization at the OPC UA service boundary. |
| `security.py` | Authentication and transport security. |
| `server.py` | Server assembly, startup ordering and graceful shutdown. |
| `settings.py` | Environment overlay and profile rules. |
| `validation.py` | Configuration loading and validation. |

## Configuration and commands

| Path | Purpose |
|---|---|
| `config/server.yaml` | Endpoint, profile, security, health |
| `config/namespaces.yaml` | Generated exact legacy namespace indexes and URIs |
| `config/namespaces.extra.yaml` | Optional additive namespaces for new equipment |
| `config/devices/*.yaml` | Generated legacy inventory (objects and variables) |
| `config/permissions.yaml` | Role matrix and denied patterns |
| `legacy/server_opcua.py` | Archived original implementation |
| `scripts/migrate_legacy.py` | AST extraction and static/runtime comparison |
| `scripts/export_nodes.py` | Address-space export used for parity fixtures |
| `scripts/generate_certificates.py` | Self-signed server certificate (0600 key) |
| `scripts/healthcheck.py` | OPC UA-aware container health check |

```bash
python -m glados_opcua --validate              # load and validate configuration
python -m glados_opcua --docs docs/index.md    # regenerate this page
python -m glados_opcua.docs --check            # fail if this page is stale
python -m glados_opcua                          # run the server
pytest                                          # compatibility and security tests
```
