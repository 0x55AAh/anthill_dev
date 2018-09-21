#!/usr/bin/env python3
"""Creates or updates geoip2 mmdb databases."""
import argparse
import requests
import tarfile
import os


products = ['City', 'Country']
link_tpl = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-%(product)s.tar.gz'
links = [link_tpl % {'product': product} for product in products]


CHUNCK_SIZE = 1024
PROGRESS_WIDTH = 30


def progress(message, width=PROGRESS_WIDTH):
    def decorator(func):
        def wrapper(*args_, **kwargs_):
            dots = width - len(message) - 7
            print('  \_ %s %s' % (message, '.' * dots), end=' ')
            func(*args_, **kwargs_)
            print('OK')
        return wrapper
    return decorator


def get_names(link, base):
    arc_name = link.rpartition('/')[-1]
    db_name = arc_name.partition('.')[0] + '.mmdb'

    return (
        os.path.join(base, arc_name),
        os.path.join(base, db_name)
    )


def main(base):
    for link in links:
        arc_name, db_name = get_names(link, base)

        print('* %s' % link)

        @progress('Downloading')
        def download():
            resp = requests.get(link, stream=True)
            with open(arc_name, 'wb') as af:
                for chunk in resp.iter_content(chunk_size=CHUNCK_SIZE):
                    af.write(chunk)

        @progress('Extracting')
        def extract():
            arc = tarfile.open(arc_name)
            for m in arc.getmembers():
                if m.name.endswith('.mmdb'):
                    with open(db_name, 'wb') as f:
                        f.write(arc.extractfile(m).read())
            arc.close()

        @progress('Cleanup')
        def cleanup():
            os.unlink(arc_name)

        download()
        extract()
        cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', dest='path', default='', help='Path where files to save', type=str)
    args = parser.parse_args()
    main(base=args.path)
