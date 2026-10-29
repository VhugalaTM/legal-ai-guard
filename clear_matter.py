import sys
from ingest import delete_matter

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clear_matter.py <matter_name>")
        sys.exit(1)
    delete_matter(sys.argv[1])