# Parallel Data Upload & Download with Cloud Storage + Custom API Integration

This project demonstrates sequential vs parallel upload/download with Supabase Storage and a custom API layer. It also works in local demo mode if you want to verify everything before deploying.

## What is included

- `generate_samples.py` creates sample text files.
- `upload_download.py` runs sequential and parallel upload/download tests.
- `api/server.js` runs a local Express API.
- `api/files.js` and `api/download.js` are Vercel serverless routes.
- `api/storage-helper.js` centralizes storage access.
- `vercel.json` exposes `/files` and `/download/:filename` as friendly routes.

## What the project compares

- Sequential upload
- Parallel upload
- Sequential download
- Parallel download
- API-based download

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- A Supabase project with a storage bucket
- A `.env` file in the project root

## 1) Set up Supabase

1. Create a free Supabase account and a new project.
2. Open `Project Settings -> API`.
3. Copy the `Project URL` into `SUPABASE_URL`.
4. Copy the `anon public` key into `SUPABASE_KEY`.
5. Create a bucket in `Storage` and copy its name into `BUCKET_NAME`.

Example `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-or-service-key
BUCKET_NAME=lab5
API_BASE_URL=http://localhost:3001
LOCAL_STORAGE_FOLDER=samples
PORT=3001
```

## 2) Install dependencies

Run these from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd api
npm install
cd ..
```

## 3) Generate sample files

Create 10 to 20 files for the assignment:

```powershell
python generate_samples.py --count 20 --out samples
```

For quick tests, you can use the smaller folder already in the repo:

```powershell
python generate_samples.py --count 3 --out samples_test
```

## 4) Run the API locally

The API can run in Supabase-backed mode or local folder mode.

Start it from the project root:

```powershell
node api/server.js
```

If the default port is busy, use another one:

```powershell
$env:PORT=3001; node api/server.js
```

The API exposes these endpoints:

- `GET /files`
- `GET /download/<filename>`

Test it quickly with:

```powershell
curl.exe http://localhost:3001/files
```

## 5) Run the benchmark script

### Local demo mode

Use this if you want to verify the workflow without relying on cloud access:

```powershell
python upload_download.py --bucket local --folder samples_test --mode all --api http://localhost:3001 --local
```

### Supabase mode

After you set `.env`, run the benchmark against your real bucket:

```powershell
python upload_download.py --bucket lab5 --folder samples --mode all --api http://localhost:3001
```

You can also run one case at a time:

- `--mode upload_seq`
- `--mode upload_par`
- `--mode download_seq`
- `--mode download_par`
- `--mode api_download`

Control concurrency with `--workers`, for example:

```powershell
python upload_download.py --bucket lab5 --folder samples --mode all --api http://localhost:3001 --workers 8
```

## 6) Deploy the API to Vercel

The API is already prepared for Vercel.

### Deploy steps

1. Push this repository to GitHub.
2. Create a new Vercel project from that repository.
3. Add these environment variables in Vercel:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `BUCKET_NAME`
4. Deploy the project.

### Public routes

- `https://your-app.vercel.app/files`
- `https://your-app.vercel.app/download/<filename>`

The rewrites in [vercel.json](vercel.json) map those URLs to the serverless functions.

## 7) How the benchmark works

The Python script does the following:

1. Reads the sample files from the chosen folder.
2. Uploads them one by one and records the time.
3. Uploads them using a thread pool and records the time.
4. Downloads them one by one and records the time.
5. Downloads them in parallel and records the time.
6. Downloads them through the API and records the time.

Example output:

```text
upload_sequential: 0.009s
upload_parallel: 0.139s
download_sequential: 0.004s
download_parallel: 0.005s
api_download: 0.050s
```

## 8) What to put in the report

Explain these points:

- Parallel I/O helps when network latency dominates the work.
- Parallelism can be slower for small files because thread overhead is larger than the task.
- The API layer adds overhead but is useful for control and security.
- Cloud results will usually differ from local results because network and provider limits matter.

## 9) What to submit

- Source code files
- Screenshot of the Supabase bucket
- Screenshot of the API response
- Screenshot of the benchmark output
- Short report with the timing table and observations

## 10) Troubleshooting

- If Node says a module is missing, run `cd api` then `npm install`.
- If Python says a package is missing, run `pip install -r requirements.txt` inside the virtual environment.
- If `node api/server.js` says the port is busy, use the alternate port command above.
- If the API cannot download files, confirm `LOCAL_STORAGE_FOLDER` and Supabase settings in `.env`.

## 11) Recommended run order

1. Create the Supabase bucket.
2. Fill in `.env`.
3. Install dependencies.
4. Generate sample files.
5. Start the API.
6. Run the benchmark script.
7. Deploy to Vercel.
8. Capture screenshots and write the report.
