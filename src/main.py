from recursive_copy_function import *
import os 
import shutil
from functions import *

def main():
    if not os.path.exists("public"):
        os.mkdir("public")
    recursive_copy("static", "public", clean = True)
    recursive_generate_page("content", "template.html", "public")
    
    


if __name__ == "__main__":
    main()