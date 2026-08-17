import zipfile
import os

zips = [
    "COOPERCBO.ZIP", "CERTHOSPITALENSINOBRASIL.ZIP", "HOSPFILANTROPICOSBRASIL.ZIP",
    "GESTORFEDERAL_202607.ZIP", "GERENTEADMINCONTRATOS202607.ZIP", "ESTNATJURBRASIL202607.ZIP",
    "SAUDE_INDIGENA_202607.ZIP", "SAMUBRASIL_202607.ZIP", "EQUIPESBRASIL_202607.ZIP",
    "PROFISSIONAIS_BRASIL_AC_202607.ZIP", "BASE_DE_DADOS_CNES_202606.ZIP", "SCNES4840-COMPLETA.ZIP"
]

workspace_dir = "/home/magno/unimed/dashboard-datasus-imperatriz"

print("Checking ZIP file sizes and internal CSV sizes:")
for z_name in zips:
    p = os.path.join(workspace_dir, z_name)
    if os.path.exists(p):
        size_mb = os.path.getsize(p) / (1024 * 1024)
        print(f"\n=== {z_name} ({size_mb:.2f} MB) ===")
        with zipfile.ZipFile(p) as z:
            csv_infos = [info for info in z.infolist() if info.filename.lower().endswith(".csv")]
            # Sort by file size descending
            csv_infos = sorted(csv_infos, key=lambda x: x.file_size, reverse=True)
            for info in csv_infos[:5]:
                print(f"  - {info.filename}: {info.file_size / (1024 * 1024):.2f} MB")
            if len(csv_infos) > 5:
                print(f"  - ... and {len(csv_infos) - 5} more files")
    else:
        print(f"\n=== {z_name} NOT FOUND ===")
