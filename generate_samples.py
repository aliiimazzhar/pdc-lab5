import os
import argparse
import random
import string


def gen_text(kb=1):
    return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=kb * 1024))


def main(count, out):
    os.makedirs(out, exist_ok=True)
    for i in range(1, count + 1):
        path = os.path.join(out, f'sample_{i:03}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(gen_text(kb=1))
    print(f'Wrote {count} files to {out}')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, default=20)
    p.add_argument('--out', type=str, default='samples')
    args = p.parse_args()
    main(args.count, args.out)
