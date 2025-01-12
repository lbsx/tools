import sys
import time
 
 
for i in range(5):
    sys.stdout.write('Processing {}\n'.format(i))
    sys.stdout.flush()
    time.sleep(1)
    if i % 2 == 0:
        sys.stderr.write('[ERROR] some wrong happened')
        sys.stderr.flush()
 