from recursive_copy_function import *
import os 
import shutil

def main():
    if not os.path.exists("public"):
        os.mkdir("public")
    recursive_copy("static", "public", clean = True)


if __name__ == "__main__":
    main()