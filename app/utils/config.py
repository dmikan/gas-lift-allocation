from pathlib import Path

def get_project_root():
    root_path = Path(__file__).parent.parent.parent
    return root_path

if __name__ == "__main__":
    root_path = get_project_root()
    print(f"Project root path: {root_path}")