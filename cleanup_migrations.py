import os

# Remove problematic migration files
migrations_dir = r"c:\Users\ADMIN\Desktop\foodproject\marketplace\migrations"

files_to_remove = [
    "0003_alter_tax_options.py",
    "0003_fix_tax_model.py", 
    "0003_migration_fix.py",
    "0008_remove_tax_category_remove_tax_exemptions_and_more.py",
    "temp_cleanup.py"
]

for file in files_to_remove:
    file_path = os.path.join(migrations_dir, file)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Failed to remove {file}: {e}")
    else:
        print(f"File not found: {file}")

print("Cleanup complete!")
