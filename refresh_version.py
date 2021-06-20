from datetime import date
import os
with open("__about__.py") as about:
    with open("__temp_about__.py", "w") as temp_about:
        for line in about.readlines():
            if line.count("__version__"):
                temp_about.write(f'__version__ = "{date.today().isoformat()}"\n')
                continue
            temp_about.write(f"{line}")

os.remove("__about__.py")
os.rename("__temp_about__.py", "__about__.py")
