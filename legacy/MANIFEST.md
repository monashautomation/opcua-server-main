# Legacy archive record

| Field | Value |
|---|---|
| File | `legacy/server_opcua.py` |
| SHA-256 | `15c30f8b443610dfc7a711ec2149cefe7477ee1e390435da4b796ab6d06d0487` |
| Static calls | 18 `add_object`, 488 `add_variable`, 482 `set_writable` |
| Runtime used for baseline | Python 3.12.12, `asyncua==1.1.8` |
| Baseline export | `tests/fixtures/legacy_nodes.json` (506 custom nodes) |
| Runtime NamespaceArray | `["http://opcfoundation.org/UA/", "urn:freeopcua:python:server"]` |
| Endpoint | `opc.tcp://<host>:4840/server/` (`GLADOS_SERVER_URL` override) |
| Server name | `DTL Local OPC UA Server Test` |

## Observed legacy quirks preserved verbatim

- NodeIDs with and without trailing semicolons, e.g. `ns=21;s=R1d_Joi1;` vs
  `ns=2;s=LabCount` and `ns=11;s=P1d_APIresp`.
- Object browse names use the object namespace (e.g. `Printer1` at ns 11);
  variable browse names use namespace 0.
- Four variables are `Int64` because they were created from bare Python ints:
  `R3d_BaseA`, `C1d_Img_h`, `C1d_Img_w`, `RGBc_ProgID`.
- `C1d_Img` and `RGBc_Img` default to `ByteString(00000000)`.
- `Operator` lives in namespace 1 (`ns=1;i=2001`).
- Six Robot 2 variables were never passed to `set_writable`: `R2c_int4`,
  `R2c_int5`, `R2c_int6`, `R2c_Bool1`, `R2c_Bool2`, `R2c_Bool3`.
- The legacy user manager accepted any password and treated the usernames
  `admin`/`Admin` as administrators.
- Secure policies were configured with no certificate, so only `NoSecurity`
  was actually served.

## Baseline method

1. Start the archived source with `GLADOS_SERVER_URL=opc.tcp://127.0.0.1:4841/server/`.
2. Export the address space with `scripts/export_nodes.py`.
3. Filter to objects whose NodeId namespace index is non-zero and their children.
4. Compare with AST extraction via `scripts/migrate_legacy.py`; zero discrepancies.

## Reproducing the baseline

```bash
python -m venv .venv && . .venv/bin/activate
pip install 'asyncua==1.1.8'
GLADOS_SERVER_URL='opc.tcp://127.0.0.1:4841/server/' python legacy/server_opcua.py &
python scripts/export_nodes.py 'opc.tcp://127.0.0.1:4841/server/' tests/fixtures/legacy_nodes.json
python scripts/migrate_legacy.py
```

Never connect two active control systems to the same physical equipment during
comparison testing.
