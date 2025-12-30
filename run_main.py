import os
import sys

# Add src to path
sys.path.append(os.path.abspath('src'))

import main

if __name__ == '__main__':
    print("Starting main via test script...")
    main.main()
    print("Main finished.")
