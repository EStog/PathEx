import os
import os.path as path
import subprocess
import re

def test_multiprocessing():
    root = path.dirname(__file__)
    file_name = path.basename(__file__)
    pattern = re.compile(r'.*\.runtest')

    for file in os.listdir(root):
        if file != file_name and re.match(pattern, file):
            subprocess.run(['python', f'{root}/{file}'], check=True)

if __name__ == '__main__': # pragma: no cover
    test_multiprocessing()
