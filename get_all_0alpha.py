import sys

from ftplib import FTP
from time import time
from urllib.request import urlretrieve
from pathlib import Path

import numpy as np

from tqdm import tqdm

ftproot = 'phoenix.astro.physik.uni-goettingen.de/HiResFITS/PHOENIX-ACES-AGSS-COND-2011/'


"""
The parameter range of the grid is

PARAMETER	RANGE	STEP SIZE
Teff [K]	2300 - 7000	100
 	7000 - 12000	200
log(g)	0.0 - 6.0	0.5
[Fe/H]	-4.0 - -2.0	1.0
 	-2.0 - +1.0	0.5
[α/M]	-0.2 - +1.2	0.2

Alpha element abundances [α/M]≠0 are available for -3.0≤[Fe/H]≤0.0. only.
"""
zz    = ['+1.0','+0.5','-0.0','-0.5','-1.0','-1.5','-2.0','-3.0','-4.0']
logg = [f'{e:<04}' for e in np.arange(0, 6.1, .5)]

teffcold = np.arange(2300, 7000, 100)
teffhot = np.arange(7000, 12001, 200)
teff = np.concatenate([teffcold,teffhot])

ftps = ['ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits']
fns = ['WAVE_PHOENIX-ACES-AGSS-COND-2011.fits']

if Path(fns[0]).is_file():
    ftps.clear()
    fns.clear()

for z in zz:
    for lg in logg:
        for t in teff:
            filename = 'lte{:05}-{}{}.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'.format(t, lg, z)
            ftppath = 'ftp://' + ftproot + 'Z' + z + '/' + filename

            if Path(filename).is_file():
                print(filename, 'already exists, skipping')
            else:
                ftps.append(ftppath)
                fns.append(filename)

                
namepairs = zip(ftps, fns)
if len(sys.argv) == 1:
    namepairs = list(namepairs)
elif len(sys.argv) == 3:
    skip = int(sys.argv[1])
    idx = int(sys.argv[2])
    namepairs = list(list(namepairs)[idx::skip])
else:
    print('Usage: get_subgrid.py [SKIP IDX]')
    sys.exit(1)



print("Checking sizes")

f = FTP(ftproot.split('/')[0])
f.login()

rootpath = ftproot.split(f.host)[-1][1:]

sizes = {}
dirs_to_visit = []
for name, info in tqdm(list(f.mlsd(rootpath))):
    if info['type'] == 'dir':
        if 'Alpha' in name:
            continue
        dir = rootpath + '/' + name
        for name, info in f.mlsd(dir):
            if info['type'] == 'file':
                sizes[name] = int(info['size'])
f.close()

nms = [nm for ftp, nm in namepairs]
sizes = {k:v for k,v in sizes.items() if k in nms}

new_namepairs = []
for ftppath, filename in namepairs:
    if filename in sizes:
        new_namepairs.append((ftppath, filename))
    else:
        print('file', filename, 'is missing from the ftp server!')

print('Total size in MB:', sum(sizes.values())/1024/1024)

for ftppath, filename in tqdm(new_namepairs):
    t1 = time()
    _, h = urlretrieve(ftppath, filename)
    t2 = time()

    print("working on ", filename, end='')
    print('\rGot ', filename,'avg speed', int(h['Content-length'])/1024/1024/(t2-t1), 'Mb/s')