import os

for root, dirs, files in os.walk("."):
    for f in files:
        try:
            with open(os.path.join(root, f), encoding="utf-8") as test_file:
                test_file.read()
        except Exception as e:
            print(f"Problem with {f}: {e}")
