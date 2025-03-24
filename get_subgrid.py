import sys

from time import time
from urllib.request import urlretrieve
from pathlib import Path

from tqdm import tqdm

ftproot = 'phoenix.astro.physik.uni-goettingen.de/HiResFITS/PHOENIX-ACES-AGSS-COND-2011/'

zz    = ['-0.0','-0.5','-1.0','-1.5','-2.0','-3.0','-4.0']
logg = ['1.00', '1.50', '2.00', '3.00','4.00', '5.00']
teff = [2500,2800,3000,3400, 3800, 4000,4200, 4400, 4600, 4800, 5000,5200,5400,5600,5800,6000,6400, 6800,7200,8000]

ftps = ['ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits']
fns = ['WAVE_PHOENIX-ACES-AGSS-COND-2011.fits']

if Path(fns[0]).is_file():
    ftps.clear()
    fns.clear()

for z in zz:
    for lg in logg:
        for t in teff:
            filename = 'lte0{}-{}{}.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'.format(t,lg,z)
            ftppath = 'ftp://' + ftproot + 'Z' + z + '/' + filename

            if Path(filename).is_file():
                print(filename, 'already exists, skipping')
            else:
                ftps.append(ftppath)
                fns.append(filename)
                
namepairs = zip(ftps, fns)
if len(sys.argv) ==1:
    namepairs = list(namepairs)
elif len(sys.argv) == 3:
    skip = int(sys.argv[1])
    idx = int(sys.argv[2])
    namepairs = list(list(namepairs)[idx::skip])
else:
    print('Usage: get_subgrid.py [SKIP IDX]')
    sys.exit(1)

for ftppath, filename in tqdm(namepairs):
    t1 = time()
    _, h = urlretrieve(ftppath, filename)
    t2 = time()

    print('got ', filename,'avg speed', int(h['Content-length'])/1024/1024/(t2-t1), 'Mb/s')