#!/usr/bin/env python3
"""Creates or updates geoip2 mmdb databases."""
import argparse
import requests
import tarfile
import os

__all__ = ['run']

products = ['City', 'Country']
link_base = 'http://geolite.maxmind.com/download/geoip/database/'
link_tpl = link_base + 'GeoLite2-%(product)s.tar.gz'
links = [link_tpl % {'product': product} for product in products]

CHUNK_SIZE = 1024
PROGRESS_WIDTH = 50


def _progress(message, width=PROGRESS_WIDTH, logger=None):
    def decorator(func):
        def wrapper(*args_, **kwargs_):
            dots = width - len(message) - 7
            if logger is None:
                print('  \_ %s %s' % (message, '.' * dots), end=' ')
            func(*args_, **kwargs_)
            if logger is None:
                print('OK')
            else:
                logger.info('  \_ %s %s OK' % (message, '.' * dots))
        return wrapper
    return decorator


def _get_names(link, base):
    arc_name = link.rpartition('/')[-1]
    db_name = arc_name.partition('.')[0] + '.mmdb'

    return (
        os.path.join(base, arc_name),
        os.path.join(base, db_name)
    )


def run(base, logger=None):
    for link in links:
        arc_name, db_name = _get_names(link, base)

        if logger is not None:
            logger.info('* %s' % link)
        else:
            print('* %s' % link)

        @_progress('Downloading', logger=logger)
        def download():
            resp = requests.get(link, stream=True)
            with open(arc_name, 'wb') as af:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    af.write(chunk)

        @_progress('Extracting', logger=logger)
        def extract():
            arc = tarfile.open(arc_name)
            for m in arc.getmembers():
                if m.name.endswith('.mmdb'):
                    with open(db_name, 'wb') as f:
                        f.write(arc.extractfile(m).read())
            arc.close()

        @_progress('Cleanup', logger=logger)
        def cleanup():
            os.unlink(arc_name)

        download()
        extract()
        cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', dest='path', default='', help='Path where files to save', type=str)
    args = parser.parse_args()
    run(base=args.path, logger=None)
