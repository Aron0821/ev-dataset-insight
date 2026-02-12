#!/usr/bin/env python3
"""
Verification script to check if all required files are in place
"""

import os
import sys


def check_file_structure():
    """Check if all required files exist"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "ARCHITECTURE.md",
        "config/__init__.py",
        "config/page_config.py",
        "utils/__init__.py",
        "utils/database.py",
        "utils/data_loader.py",
        "utils/map_debug.py",
        "utils/ml_models.py",
        "components/__init__.py",
        "components/sidebar.py",
        "components/metrics.py",
        "components/tabs/__init__.py",
        "components/tabs/trends.py",
        "components/tabs/manufacturers.py",
        "components/tabs/geographic.py",
        "components/tabs/performance.py",
        "components/tabs/data_table.py",
        "components/tabs/ai_analyst.py",
        "components/tabs/prediction.py",
        "components/tabs/forecast.py",
    ]

    print("Checking file structure...")
    print("=" * 60)

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)

    print("=" * 60)

    if missing_files:
        print(f"\n⚠️  {len(missing_files)} file(s) missing!")
        print("\nMissing files:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("\n✅ All files are in place!")
        print("\nYou can now run the dashboard with:")
        print("  streamlit run app.py")
        return True


if __name__ == "__main__":
    success = check_file_structure()
    sys.exit(0 if success else 1)
