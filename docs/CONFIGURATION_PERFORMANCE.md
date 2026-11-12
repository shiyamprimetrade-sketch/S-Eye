# Configuration, batching and bounded descriptor caching

`seye-workflow --config /path/to/config.json --request ... --output ...` accepts a
strict schema-1 policy file:

```json
{"schema_version":1,"read_roots":["/absolute/input/root"],"write_roots":["/absolute/output/root"],"memory":false,"training":false,"video":false,"timeout":30}
```

Unknown fields, nonboolean capabilities, relative roots and invalid timeouts are
rejected. CLI root lists, when supplied, replace the corresponding config roots;
explicit capability flags may enable an additional capability. Configuration is
an explicit user policy, not an untrusted request's permission grant. A pure
version-0 experimental-format migration supports allowed_directory/allow_write/
allow_memory; it never rewrites the file or invents write permission. This is not
an automatic migration of old camera/memory settings.

`recognize_batch` requests contain an explicit `model` checkpoint and `images`
list (1–100 paths), instead of a single image. Every path is checked against
read grants. A bounded per-request descriptor cache avoids repeating extraction
for duplicate source bytes, and reports hits/misses/evictions. It does not persist
across separate CLI invocations or retain input pixels.

`FeatureCache` is also available for long-lived offline Python clients. It validates
and decodes source bytes on every lookup; source-root checks still apply on hits.
Keys bind feature version and actual source SHA-256. Changed bytes invalidate the
entry; returned feature lists are defensive copies. Entry count and estimated
Python storage are bounded with LRU eviction. The byte estimate is not process RSS
or a complete native-memory measurement.

```bash
python scripts/benchmark_cache.py --output /tmp/new-cache-report.json
```

The recorded local experiment repeats one generated image 20 times: 19 hits,
1 miss, identical descriptors, 3,197 estimated cache bytes and an observed 6.66×
wall-time ratio for this descriptor path. It retains source read/hash/decode and
excludes full segmentation/detection, unique-image workloads and video analysis.
Python CPU seconds and wall time are both recorded. One host sample is not a device
performance guarantee or a stable regression threshold.

Windows and Linux CI at `acf5cbe` passed the preceding 81-test implementation on
Python 3.12 and 3.13, with actual video, install and source/release audits:
https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43263993932
New cache/config/batch tests require their own exact-head checks. Actual Android
ARM64/Termux measurements remain unavailable.

`group_objects` supplies transitive box-proximity groups in one coordinate grid.
These groups are geometric adjacency, not assertions of shared semantic identity.
Cross-session object identity and scalable descriptor indexing remain open.
