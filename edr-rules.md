# Clinejection / OpenClaw — EDR rules

**Scope:** Use only to check if you were **already compromised** in this incident or recent attacks (e.g. infected Cline 2.3.0 or openclaw). Not for future-proof protection—just to see if observed versions in your environment were exploited.

---

## 1. Malicious package.json (Cline 2.3.0)

**File:** `package.json` from the known malicious Cline 2.3.0 package (contains `"postinstall":"npm install -g openclaw@latest"`).

**SHA256:** `c2c65f4f1edc86c3645a456574ca31493c5991361ba90c0efbaf0293a14ea638`

Search your system (CrowdStrike / SentinelOne) for this file hash to find that exact package anywhere.

| Platform | Query |
|----------|--------|
| **CrowdStrike** | `Sha256Hash:'c2c65f4f1edc86c3645a456574ca31493c5991361ba90c0efbaf0293a14ea638'` |
| **SentinelOne** | `fileSha256 = "c2c65f4f1edc86c3645a456574ca31493c5991361ba90c0efbaf0293a14ea638"` (or equivalent file-hash field in your schema) |

---

## 2. OpenClaw

Search for process name, command line, or file path containing **openclaw** (e.g. `npm install -g openclaw@latest` runs from npm postinstall; parent is typically npm/node, not the AI agent).

| Platform | Query |
|----------|--------|
| **CrowdStrike** | `CommandLine:*'openclaw'*` |
| **SentinelOne** | `processCmd contains "openclaw"` |

---

**Disclaimer:** These rules are for scanning for the **current incident and recent attacks** to determine if you were compromised. They are not intended for ongoing or future threat prevention—only to see whether versions present in your systems were already exploited.
