import shutil
import subprocess
import zipfile
from pathlib import Path

# ============================
# CONFIGURACIÓN
# ============================

ROOT = Path(__file__).resolve().parents[1]  # ajustá si el script vive en otro lado

LAYER_DIR   = ROOT / "apiRest" / "layer"
DOMAIN_DIST = ROOT / "apiRest" / "packages" / "domain"
LAMBDAS_DIR = ROOT / "apiRest" / "lambdas"

# ============================
# UTILS
# ============================

def run(cmd: list[str], cwd: Path | None = None, optional=False):
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        if optional:
            print(f"⚠️  Command failed (ignored): {' '.join(cmd)}")
        else:
            raise e


def zip_dir(src: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in src.rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(src))


# ============================
# 1️⃣ BUILD DOMAIN
# ============================

print("🔧 Building @game/domain...")
run(["pnpm", "--filter", "@game/domain", "build"])

# ============================
# 2️⃣ CREATE LAMBDA LAYER
# ============================

print("📦 Packaging Lambda Layer...")

if LAYER_DIR.exists():
    shutil.rmtree(LAYER_DIR)

nodejs_path = LAYER_DIR / "nodejs"
domain_layer_path = nodejs_path / "node_modules" / "@game" / "domain"

domain_layer_path.mkdir(parents=True, exist_ok=True)

# node_modules (deps del domain)
shutil.copytree(
    DOMAIN_DIST / "node_modules",
    nodejs_path / "node_modules",
    dirs_exist_ok=True
)

# dist
shutil.copytree(
    DOMAIN_DIST / "dist",
    domain_layer_path / "dist",
    dirs_exist_ok=True
)

# package.json
shutil.copy2(
    DOMAIN_DIST / "package.json",
    domain_layer_path / "package.json"
)

zip_path = LAYER_DIR / "domain-layer.zip"
if zip_path.exists():
    zip_path.unlink()

zip_dir(LAYER_DIR, zip_path)

# ============================
# 3️⃣ BUILD + PACKAGE LAMBDAS
# ============================

for lambda_dir in LAMBDAS_DIR.iterdir():
    if not lambda_dir.is_dir():
        continue

    lambda_name = lambda_dir.name
    print(f"🚀 Packaging lambda: {lambda_name}")

    # Build (opcional)
    run(
        ["pnpm", "--filter", lambda_name, "build"],
        optional=True
    )

    dist_dir = lambda_dir / "dist"
    pkg_dir  = lambda_dir / "package"
    zip_file = lambda_dir / f"{lambda_name}.zip"

    if not dist_dir.exists():
        print(f"⏭️  No dist/ found for {lambda_name}, skipping packaging")
        continue

    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)

    pkg_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(dist_dir, pkg_dir, dirs_exist_ok=True)

    if zip_file.exists():
        zip_file.unlink()

    zip_dir(pkg_dir, zip_file)

print("✅ Packaging completo!")
