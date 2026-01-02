import subprocess
import sys
import os

os.chdir('/media/DATA/projects/autonomous-coding-uno-bot/unobot/client')
subprocess.Popen([sys.executable, '-m', 'pnpm', 'dev'], 
                 stdout=open('frontend.log', 'w'), 
                 stderr=subprocess.STDOUT)
print('Frontend started')
