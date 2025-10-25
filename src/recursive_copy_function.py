import os
import shutil



def recursive_copy(src, dst, clean=True):
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source not found: {src}")
    if not os.path.exists(dst):
        raise FileNotFoundError(f"Target directory not found: {dst}")
    if clean:
        for name in os.listdir(dst):
            print(f"deleting {name} from {dst}")
            p = os.path.join(dst, name)
            if os.path.isfile(p):
                os.remove(p)
            else:
                shutil.rmtree(p)
    for name in os.listdir(src):
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.isfile(s):
            shutil.copy(s, d)
            print(f"copied file from {s} to {d}")
        elif os.path.isdir(s):
            os.mkdir(d)
            print(f"made directory {d} and beginning a new recursion")
            recursive_copy(s, d, clean=False)

