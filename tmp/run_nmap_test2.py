import sys, os
sys.path.append(os.path.abspath('.'))
from tools.cyber_helper import run_nmap_scan
print(run_nmap_scan('localhost'))
