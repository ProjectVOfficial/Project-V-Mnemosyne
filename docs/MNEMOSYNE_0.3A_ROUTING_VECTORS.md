# Mnemosyne 0.3a — Routing Test Vectors

Status: **implementation gate**

Phoenix 0.3a introduces a pure bank resolver only. No live retain/recall behavior
is changed in this gate.

## Contract

Base bank:

```text
phoenix-mnemosyne-03-routing-test
```

Equivalent Windows workspace spellings must resolve to the same bank:

```text
D:\PROJECTS\Phoenix-Desktop
d:/projects/phoenix-desktop/
```

Expected route:

```text
phoenix-mnemosyne-03-routing-test-ws-phoenix-desktop-a4a9e477801c
```

A different workspace must resolve to a different bank:

```text
D:\PROJECTS\Project-V-Mnemosyne
```

Expected route:

```text
phoenix-mnemosyne-03-routing-test-ws-project-v-mnemosyne-14281d58c797
```

## Required properties

- global scope resolves to the configured base bank
- working-directory scope with an absolute workspace path resolves to a deterministic workspace bank
- equivalent Windows path casing/slash/trailing-separator variants resolve identically
- distinct workspaces resolve differently
- missing or relative workspace paths fail closed to the base bank
- active-workspace recall planning returns base + workspace banks
- generated bank IDs contain only Hindsight/Phoenix-safe characters
- generated bank IDs are at most 160 characters
- generated bank IDs do not expose the full absolute workspace path

## Hash identity

The workspace suffix uses the first 12 hexadecimal characters of SHA-256 over:

```text
<normalized base bank> + NUL + <normalized lowercase Windows workspace path>
```

The human-readable workspace slug is cosmetic; the hash carries the stable
workspace identity.

## Safety

This resolver carries no permission or authorization state. Memory remains
context only. 0.2 metadata authority normalization remains unchanged.
