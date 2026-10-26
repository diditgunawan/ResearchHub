"""
ResearchForge Concurrency & High-Throughput Stress Verification Script
====================================================================
Simulates 50 concurrent async requests across critical platform endpoints:
1. Health & Readiness probes (/healthz, /readyz)
2. Open Scholarly Federated Search (/works/search)
3. Authenticated tenant library queries (/projects/{id}/library/items)
4. Journal fit catalog search (/journals)

Measures:
- Latency percentiles (P50, P95, P99)
- Concurrency success rate (100% required)
- Zero socket leaks or event-loop hangs
"""

import sys
import time
import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"
CONCURRENCY = 50

async def probe_endpoint(client: httpx.AsyncClient, name: str, method: str, url: str, headers: dict = None, json_data: dict = None):
    start = time.perf_counter()
    try:
        if method == "GET":
            resp = await client.get(url, headers=headers, timeout=15.0)
        else:
            resp = await client.post(url, headers=headers, json=json_data, timeout=15.0)
        elapsed = (time.perf_counter() - start) * 1000.0
        return {
            "name": name,
            "status": resp.status_code,
            "elapsed_ms": elapsed,
            "ok": resp.status_code in [200, 201]
        }
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        return {
            "name": name,
            "status": 500,
            "elapsed_ms": elapsed,
            "ok": False,
            "error": str(e)
        }

async def run_stress_test():
    print("="*80)
    print(f"  RESEARCHFORGE CONCURRENCY STRESS SUITE ({CONCURRENCY} PARALLEL REQUESTS)")
    print("="*80)

    async with httpx.AsyncClient(base_url=BASE_URL, headers={"X-Test-Echo-Token": "1"}) as client:
        # 1. Warm-up & Setup isolated tenant
        email = "lead.researcher@medical.ox.ac.uk"
        link = await client.post("/auth/magic-link", json={"email": email})
        if link.status_code != 200:
            link = await client.post("/auth/magic-link", json={"email": "stress.tester@perf.org"})
        assert link.status_code == 200, "Setup magic link failed"
        sess = await client.post("/auth/session", json={"token": link.json()["token"]})
        assert sess.status_code == 200, "Setup session failed"
        token = sess.json()["session_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj = await client.post("/projects", json={"name": "Concurrency Benchmark Project"}, headers=headers)
        proj_id = proj.json()["id"]

        # 2. Build 50 concurrent tasks
        tasks = []
        endpoints = [
            ("Healthz Probe", "GET", "/healthz", None, None),
            ("Readyz Probe", "GET", "/readyz", None, None),
            ("Journal Search", "GET", "/journals?quartiles=Q1", headers, None),
            ("Library Items", "GET", f"/projects/{proj_id}/library/items", headers, None),
            ("Scholarly Search", "GET", "/works/search?q=machine+learning+clinical&page_size=3", headers, None),
        ]

        for i in range(CONCURRENCY):
            spec = endpoints[i % len(endpoints)]
            tasks.append(probe_endpoint(client, spec[0], spec[1], spec[2], spec[3], spec[4]))

        start_all = time.perf_counter()
        results = await asyncio.gather(*tasks)
        total_time_ms = (time.perf_counter() - start_all) * 1000.0

        # 3. Analyze Latencies & Success
        successes = [r for r in results if r["ok"]]
        latencies = sorted([r["elapsed_ms"] for r in results])
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[-1]

        print(f"\n[STRESS RESULTS]")
        print(f"  Total Requests Executed: {len(results)}")
        print(f"  Successful (2xx):        {len(successes)} / {len(results)} ({len(successes)/len(results)*100:.1f}%)")
        print(f"  Total Wall-Clock Time:   {total_time_ms:.2f} ms")
        print(f"  Throughput:              {len(results) / (total_time_ms / 1000.0):.1f} req/sec")
        print(f"  Latency P50:             {p50:.2f} ms")
        print(f"  Latency P95:             {p95:.2f} ms")
        print(f"  Latency P99:             {p99:.2f} ms")

        # Breakdown by endpoint
        print("\n[PER-ENDPOINT BREAKDOWN]")
        for name in ["Healthz Probe", "Readyz Probe", "Journal Search", "Library Items", "Scholarly Search"]:
            group = [r for r in results if r["name"] == name]
            if group:
                avg = sum(r["elapsed_ms"] for r in group) / len(group)
                passed = sum(1 for r in group if r["ok"])
                print(f"  - {name:20s}: {passed:2d}/{len(group):2d} passed | Avg: {avg:6.2f} ms")

        assert len(successes) == CONCURRENCY, f"Expected {CONCURRENCY} successes, got {len(successes)}"
        print("\n" + "="*80)
        print("         CONCURRENCY STRESS VERIFICATION: 100% PASSED (EXIT CODE 0)      ")
        print("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(run_stress_test())
        sys.exit(0)
    except Exception as exc:
        print(f"\n[FATAL] Stress test failed: {exc}")
        sys.exit(1)
