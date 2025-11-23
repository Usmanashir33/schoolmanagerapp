import os
import sys
import shutil

def replace_in_file(file_path, old, new):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(old, new)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Could not update {file_path}: {e}")

def rename_folder(old_folder, new_folder):
    if os.path.exists(old_folder):
        shutil.move(old_folder, new_folder)
        print(f"✓ Renamed folder: {old_folder} → {new_folder}")
    else:
        print(f"✗ Folder '{old_folder}' not found — skipped")

def scan_and_replace(root_path, old, new):
    allowed_ext = (".py", ".txt", ".html", ".env", ".cfg", ".ini", ".md")
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(allowed_ext):
                file_path = os.path.join(root, file)
                replace_in_file(file_path, old, new)

def main():
    if len(sys.argv) < 3:
        print("Usage: python rename_backproject.py old_name new_name")
        sys.exit(1)

    old_name = sys.argv[1]
    # 🔥 force lowercase backproject name
    new_name = sys.argv[2]

    print(f"\n🔄 Renaming Django backproject: {old_name} → {new_name}\n")

    rename_folder(old_name, new_name)

    core_files = [
        os.path.join(new_name, "settings.py"),
        os.path.join(new_name, "wsgi.py"),
        os.path.join(new_name, "asgi.py"),
        "manage.py",
    ]

    for file in core_files:
        if os.path.exists(file):
            replace_in_file(file, old_name, new_name)
            print(f"✓ Updated imports in {file}")

    apps_to_rename = []

    for app in apps_to_rename:
        rename_folder(app, app)

    print("\n📂 Updating imports everywhere…\n")
    scan_and_replace(".", old_name, new_name)

    print("\n🎉 DONE! Django backproject renamed successfully.\n")

if __name__ == "__main__":
    main()
