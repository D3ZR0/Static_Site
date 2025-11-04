from recursive_copy_function import *
import os 
import shutil
from functions import *
import sys

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    if not os.path.exists("docs"):
        os.mkdir("docs")
    recursive_copy("static", "docs", clean = True)
    recursive_generate_page("content", "template.html", "docs", basepath)
    
    


if __name__ == "__main__":
    main()