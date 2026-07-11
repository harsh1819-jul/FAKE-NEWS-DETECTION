import os
import sys

def verify_project():
    """
    Sanity checks for TruthLens Phase 1 file structure and module imports.
    Using ASCII characters to prevent terminal encoding errors.
    """
    print("=" * 60)
    print("TruthLens Project Verification Script (Phase 1)")
    print("=" * 60)

    # Get project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Project root: {root_dir}")

    # 1. Check directories
    required_dirs = [
        "database", "logs", "uploads", "cleaned_data",
        "models", "reports", "pages", "services", "utils", "tests", "assets", ".streamlit"
    ]
    
    missing_dirs = []
    for d in required_dirs:
        path = os.path.join(root_dir, d)
        if os.path.isdir(path):
            print(f"[OK] Directory exists: {d}/")
        else:
            print(f"[ERROR] Directory missing: {d}/")
            missing_dirs.append(d)

    # 2. Check files
    required_files = [
        "app.py", "requirements.txt", "README.md",
        os.path.join(".streamlit", "config.toml"),
        os.path.join("assets", "style.css"),
        os.path.join("assets", "logo.svg"),
        os.path.join("services", "logger.py"),
        os.path.join("utils", "ui_components.py"),
        os.path.join("pages", "home.py"),
        os.path.join("pages", "settings.py"),
        os.path.join("pages", "upload.py"),
        os.path.join("pages", "preparation.py"),
        os.path.join("pages", "dashboard.py"),
        os.path.join("pages", "training.py"),
        os.path.join("pages", "detect.py"),
        os.path.join("pages", "reports_page.py")
    ]

    missing_files = []
    for f in required_files:
        path = os.path.join(root_dir, f)
        if os.path.isfile(path):
            print(f"[OK] File exists: {f}")
        else:
            print(f"[ERROR] File missing: {f}")
            missing_files.append(f)

    # 3. Import tests
    print("-" * 60)
    print("Running Python Import Checks...")
    print("-" * 60)
    
    sys.path.insert(0, root_dir)
    
    try:
        from services.logger import logger
        print("[OK] Successfully imported services.logger")
    except Exception as e:
        print(f"[ERROR] Failed to import services.logger: {str(e)}")
        sys.exit(1)

    try:
        from utils.ui_components import load_css, render_phase2_preview
        print("[OK] Successfully imported utils.ui_components")
    except Exception as e:
        print(f"[ERROR] Failed to import utils.ui_components: {str(e)}")
        sys.exit(1)

    print("=" * 60)
    if not missing_dirs and not missing_files:
        print("SUCCESS: All Phase 1 directories, files, and imports verified!")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"FAILURE: Missing {len(missing_dirs)} directories and {len(missing_files)} files.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    verify_project()
