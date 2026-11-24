# Adding devices

Configuration is a flat, lossless inventory. Reusable templates are deliberately
not used until legacy parity is approved: a template hides exactly the per-device
exceptions (NodeID punctuation, Int64 inference, non-writable variables) that
compatibility depends on.

## Where files go

| Path | Ownership |
|---|---|
| `config/devices/01_…` … `09_…` | Generated from legacy source. Do not hand-edit. |
| `config/devices/90_extra.yaml` | Hand-authored additions, additive only. |
| `config/namespaces.yaml` | Generated legacy namespace indexes 0–53. |
| `config/namespaces.extra.yaml` | Optional extra namespaces for new equipment. |

CI regenerates the nine legacy files and compares them; hand-authored files are
ignored by that check. Never renumber or reuse a legacy namespace index.

## Object and variable YAML

```yaml
config_version: 1
equipment:
  - name: robot5
    namespace: 25                 # must exist in namespaces.extra.yaml
    node_id: 'ns=25;i=1'          # explicit object NodeId
    browse_namespace: 25          # legacy convention for object browse names
    description: KUKA KMR iiwa 14 R820 (added)
    variables:
      - browse_name: R5c_Start
        node_id: 'ns=25;s=R5c_Start;'
        browse_namespace: 0       # variables use namespace 0
        data_type: Boolean
        default: false
        value_rank: -1            # scalars only; arrays need separate approval
        writable: true
        category: command
        writer: controller
```

Add the namespace in `config/namespaces.extra.yaml`:

```yaml
namespaces:
  - index: 25
    uri: urn:glados:opcua:robot5
    kind: equipment
```

## Rules that are enforced

- NodeIDs are literal; trailing semicolons are part of the identifier.
- The variable NodeId must be in the equipment's object namespace.
- Browse names must be unique within an object. Variables normally use
  namespace 0, objects use the equipment namespace.
- `data_type` is explicit. A bare Python integer is **not** an Int32: legacy
  bare ints became Int64. Choose the type deliberately.
- `default` must match the declared type. ByteStrings are YAML lists of bytes.
- `value_rank` must be `-1`; array support requires its own compatibility review.
- `writable: false` is preserved even for administrators.
- `writer` is the production write owner: `device`, `controller` or `admin`
  (unconfirmed ownership). `category` is documentation and review metadata.

## Permissions

`writer` is enforced through `config/permissions.yaml`:

- `device` role writes variables with `writer: device`, scoped by each user's
  `equipment` list.
- `controller` writes `writer: controller`.
- `admin` writes all writable variables; unconfirmed ownership stays admin-only.
- `monitor` is read-only.

After editing, teach the role matrix nothing new unless you introduce a new role.
Add users in `security.users` with `password_env` or a client `certificate`.

## Verify

```bash
python -m glados_opcua --validate
python -m glados_opcua --docs docs/index.md   # regenerate the reference page
python -m glados_opcua.docs --check           # CI drift gate
pytest -q
```

New nodes are additive; the compatibility test compares only the frozen legacy
nodes. Existing NodeIDs and browse paths must remain untouched.
