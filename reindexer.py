# Rudolph, the red-nosed reindexer...
import os

data_dirs = os.walk("./data/")
print(f'objects from walk are: {data_dirs}')
print("The full walk data is:")
for root, dirs, files in data_dirs:
    print(f'at root {root}:')
    print("   files:")
    for name in files:
        print(os.path.join(root, name))
    print("   dirs:")
    for name in dirs:
        print(os.path.join(root, name))