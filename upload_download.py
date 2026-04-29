import os
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from supabase import create_client
except Exception:
    create_client = None
import requests
import asyncio
import aiohttp
from dotenv import load_dotenv
from tqdm import tqdm
import shutil
import pathlib

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
LOCAL_STORAGE_FOLDER = os.environ.get('LOCAL_STORAGE_FOLDER', 'local_storage')

use_local_default = not (SUPABASE_URL and SUPABASE_KEY and BUCKET_NAME and create_client)
if not use_local_default:
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    storage = sb.storage()
else:
    storage = None


def list_local_files(folder):
    files = []
    for root, _, filenames in os.walk(folder):
        for name in filenames:
            files.append(os.path.join(root, name))
    return files


def upload_file_supabase(bucket, local_path, dest_path):
    with open(local_path, 'rb') as f:
        data = f.read()
    res = storage.from_(bucket).upload(dest_path, data)
    return res


def upload_file_local(bucket, local_path, dest_path):
    # dest_path is treated as relative path inside LOCAL_STORAGE_FOLDER
    dst_root = pathlib.Path(LOCAL_STORAGE_FOLDER)
    dst_root.mkdir(parents=True, exist_ok=True)
    dst = dst_root.joinpath(os.path.basename(dest_path))
    shutil.copy2(local_path, dst)
    return {'result': 'ok', 'path': str(dst)}


def upload_file(bucket, local_path, dest_path, local_mode=False):
    if local_mode or storage is None:
        return upload_file_local(bucket, local_path, dest_path)
    return upload_file_supabase(bucket, local_path, dest_path)


def download_file_supabase(bucket, key, out_folder):
    data = storage.from_(bucket).download(key)
    os.makedirs(out_folder, exist_ok=True)
    out_path = os.path.join(out_folder, os.path.basename(key))
    with open(out_path, 'wb') as f:
        f.write(data)
    return out_path


def download_file_local(bucket, key, out_folder):
    src = pathlib.Path(LOCAL_STORAGE_FOLDER).joinpath(os.path.basename(key))
    if not src.exists():
        raise FileNotFoundError(str(src))
    os.makedirs(out_folder, exist_ok=True)
    dst = pathlib.Path(out_folder).joinpath(src.name)
    shutil.copy2(src, dst)
    return str(dst)


def download_file(bucket, key, out_folder, local_mode=False):
    if local_mode or storage is None:
        return download_file_local(bucket, key, out_folder)
    return download_file_supabase(bucket, key, out_folder)


def upload_sequential(bucket, files, prefix='', workers=8, local_mode=False):
    start = time.perf_counter()
    for path in files:
        name = os.path.join(prefix, os.path.basename(path))
        upload_file(bucket, path, name, local_mode=local_mode)
    return time.perf_counter() - start


def upload_parallel(bucket, files, prefix='', workers=8, local_mode=False):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(upload_file, bucket, p, os.path.join(prefix, os.path.basename(p)), local_mode): p for p in files}
        for fut in tqdm(as_completed(futures), total=len(futures)):
            fut.result()
    return time.perf_counter() - start


def download_sequential(bucket, keys, out_folder='downloads', local_mode=False):
    start = time.perf_counter()
    for key in keys:
        download_file(bucket, key, out_folder, local_mode=local_mode)
    return time.perf_counter() - start


def download_parallel_threads(bucket, keys, out_folder='downloads', workers=8, local_mode=False):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(download_file, bucket, k, out_folder, local_mode): k for k in keys}
        for fut in tqdm(as_completed(futures), total=len(futures)):
            fut.result()
    return time.perf_counter() - start


async def download_via_api_async(base_url, keys, out_folder='downloads_api'):
    os.makedirs(out_folder, exist_ok=True)
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for k in keys:
            url = f"{base_url.rstrip('/')}/download/{os.path.basename(k)}"
            tasks.append(session.get(url))
        responses = await asyncio.gather(*tasks)
        for i, r in enumerate(responses):
            if r.status == 200:
                data = await r.read()
                path = os.path.join(out_folder, os.path.basename(keys[i]))
                with open(path, 'wb') as f:
                    f.write(data)
    return time.perf_counter() - start


def get_bucket_keys(bucket, prefix=''):
    if storage is None:
        # local folder
        p = pathlib.Path(LOCAL_STORAGE_FOLDER)
        if not p.exists():
            return []
        return [str(x.name) for x in p.iterdir() if x.is_file()]
    res = storage.from_(bucket).list(prefix)
    # res is expected to be list of dicts with 'name'
    keys = [item['name'] for item in res]
    return keys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bucket', required=True)
    p.add_argument('--folder', default='samples')
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--mode', choices=['upload_seq','upload_par','download_seq','download_par','api_download','all'], default='all')
    p.add_argument('--api', help='API base URL for API download tests')
    p.add_argument('--local', action='store_true', help='Use local filesystem mode (no cloud)')
    args = p.parse_args()

    files = list_local_files(args.folder)
    keys = [os.path.basename(f) for f in files]
    local_mode = args.local or (storage is None)

    results = {}

    if args.mode in ('upload_seq','all'):
        t = upload_sequential(args.bucket, files, workers=args.workers, local_mode=local_mode)
        results['upload_sequential'] = t
        print('upload_sequential', t)

    if args.mode in ('upload_par','all'):
        t = upload_parallel(args.bucket, files, workers=args.workers, local_mode=local_mode)
        results['upload_parallel'] = t
        print('upload_parallel', t)

    if args.mode in ('download_seq','all'):
        t = download_sequential(args.bucket, keys, local_mode=local_mode)
        results['download_sequential'] = t
        print('download_sequential', t)

    if args.mode in ('download_par','all'):
        t = download_parallel_threads(args.bucket, keys, workers=args.workers, local_mode=local_mode)
        results['download_parallel'] = t
        print('download_parallel', t)

    if args.mode in ('api_download','all'):
        if not args.api:
            print('API base URL required for api_download')
        else:
            t = asyncio.run(download_via_api_async(args.api, keys))
            results['api_download'] = t
            print('api_download', t)

    print('\nSummary:')
    for k, v in results.items():
        print(f'{k}: {v:.3f}s')


if __name__ == '__main__':
    main()
