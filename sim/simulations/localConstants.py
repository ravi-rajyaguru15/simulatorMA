import os

OUTPUT_DIRECTORY = "/tmp/output"
try: os.mkdir(OUTPUT_DIRECTORY)
except FileExistsError: pass