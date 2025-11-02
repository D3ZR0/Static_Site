from recursive_copy_function import *
import os 
import shutil
from functions import *

def main():
    if not os.path.exists("public"):
        os.mkdir("public")
    recursive_copy("static", "public", clean = True)
    generate_page("content/index.md", "template.html", "public/index.html")
    


if __name__ == "__main__":
    main()