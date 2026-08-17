import zipfile
import os

zip_path = "/home/magno/unimed/dashboard-datasus-imperatriz/BASE_DE_DADOS_CNES_202606.ZIP"

print("Checking ZIP file:", zip_path)
if not os.path.exists(zip_path):
    print("Error: ZIP file not found!")
    exit(1)

try:
    with zipfile.ZipFile(zip_path) as z:
        print("Files in ZIP:", len(z.namelist()))
        csv_name = [name for name in z.namelist() if "tbEstabelecimento" in name][0]
        print("Found establishment file:", csv_name)
        with z.open(csv_name) as f:
            header = f.readline().decode('latin-1').strip()
            print("\nHeader of CSV:")
            print(header)
            first_line = f.readline().decode('latin-1').strip()
            print("\nFirst row of CSV:")
            print(first_line)
except Exception as e:
    print("Error reading zip:", e)
