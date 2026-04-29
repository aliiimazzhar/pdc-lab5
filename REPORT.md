Parallel Data Upload & Download — Short Report

Experiment setup
- Local filesystem mode used for quick verification (no Supabase credentials).
- API: `api/server.js` (Express) running in local-mode serving files from `samples_test/`.
- Samples: 3 small text files created in `samples_test/` using `generate_samples.py`.
- Script: `upload_download.py` runs sequential and parallel upload/download tests and an API-based download.

Timings (single run, local mode)
- upload_sequential: 0.009 s
- upload_parallel: 0.139 s
- download_sequential: 0.004 s
- download_parallel: 0.005 s
- api_download: 0.050 s

Observations
- For very small files and a tiny dataset (3 files), sequential operations appear faster than parallel in this run for uploads. This is due to thread scheduling and overhead: creating threads and coordinating futures adds measurable overhead that dominates for trivial work.
- Downloads show near-identical times for sequential and parallel on local filesystem: reading small files is extremely fast and parallelism doesn't help.
- API-based download measured ~0.05s total; the API proxy adds overhead (HTTP request handling + file streaming) compared to direct filesystem reads, but with networked cloud storage the balance may differ.

Analysis (general, for real cloud runs)
- Parallelism benefits I/O-bound operations when each operation has significant latency (network transfer, remote API latency). For large files or high-latency networks, parallel uploads/downloads can saturate bandwidth and reduce wall-clock time.
- Overheads that reduce parallel speedups:
  - Thread/process creation and synchronization costs
  - Per-request latency (TCP handshake, TLS) which can be amortized by persistent connections or HTTP/2
  - API rate limits or per-client concurrency limits (cloud provider or custom API)
  - Local CPU and disk contention when many concurrent operations run
- API layer effect:
  - Adds CPU and network overhead on the server side (proxying increases latency per request)
  - Can centralize authentication and access control, which is valuable despite some overhead
  - If deployed on a low-resource server or behind rate-limited infrastructure (serverless cold starts), API layer can become a bottleneck

Recommendations for full exercise
1. Use 10–20 files of varying sizes (e.g., 100KB, 1MB, 10MB) to observe scaling.
2. Run tests against real Supabase (or S3/Azure) rather than local files to measure network effects.
3. Try different concurrency settings (`--workers`) and measure throughput and errors.
4. Capture screenshots of:
   - Cloud bucket listing and uploaded files
   - API `/files` and `/download/:filename` responses
   - Terminal output with timing summary
5. Write a 1–2 page report combining these results, the table of timings, and conclusions about bottlenecks.

Files in this workspace
- [README.md](README.md) — setup and quick-start
- [generate_samples.py](generate_samples.py) — create sample files
- [upload_download.py](upload_download.py) — experiment script
- [api/server.js](api/server.js) — Express API (local-mode fallback)
- [.env.example](.env.example)

Next steps you can run now
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1
# Generate samples
python generate_samples.py --count 20 --out samples
# Start API (local mode)
cd api
npm start
# In another shell, run experiments against real Supabase (set env vars or use .env)
cd ..
python upload_download.py --bucket YOUR_BUCKET --folder samples --mode all --api http://localhost:3000
```

If you want, I can:
- Deploy the API to Vercel with Git integration and give a public URL
- Add S3 / Azure support switches and helper notes for students
- Run a full experiment against Supabase if you provide credentials or allow me to help configure them
