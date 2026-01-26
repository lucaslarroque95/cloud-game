#!/usr/bin/env python3
"""
Script para empaquetar y subir las funciones Lambda a S3
Uso: python deploy-lambdas.py --bucket-name "mi-bucket-lambda" --region "us-east-1"
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def check_aws_cli():
    """Verifica que AWS CLI esté instalado"""
    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ AWS CLI encontrado: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: AWS CLI no está instalado o no está en el PATH", file=sys.stderr)
        return False


def check_or_create_bucket(bucket_name, region):
    """Verifica que el bucket existe o lo crea"""
    print(f"\n🔍 Verificando bucket S3: {bucket_name}...")
    
    # Verificar si el bucket existe
    result = subprocess.run(
        ["aws", "s3", "ls", f"s3://{bucket_name}", "--region", region],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Bucket '{bucket_name}' existe")
        return True
    
    # El bucket no existe, preguntar si crearlo
    print(f"⚠️  El bucket '{bucket_name}' no existe.")
    response = input("¿Deseas crearlo? (S/N): ").strip().upper()
    
    if response == "S":
        print(f"📦 Creando bucket {bucket_name}...")
        result = subprocess.run(
            ["aws", "s3", "mb", f"s3://{bucket_name}", "--region", region],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Bucket '{bucket_name}' creado exitosamente")
            return True
        else:
            print(f"❌ Error al crear el bucket: {result.stderr}", file=sys.stderr)
            return False
    else:
        print("❌ Operación cancelada")
        return False


def deploy_lambda(lambda_name, lambda_path, bucket_name, s3_prefix, region):
    """Empaqueta y sube una función Lambda a S3"""
    print(f"\n📦 Empaquetando {lambda_name}...")
    
    lambda_path_obj = Path(lambda_path)
    if not lambda_path_obj.exists():
        raise FileNotFoundError(f"La ruta de Lambda no existe: {lambda_path}")
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory(prefix=f"lambda-{lambda_name}-") as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copiar archivos de la función Lambda
        print(f"   Copiando archivos desde {lambda_path}...")
        for item in lambda_path_obj.iterdir():
            dest = temp_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        
        # Crear archivo ZIP
        zip_path = temp_path.parent / f"{lambda_name}.zip"
        print(f"   Creando ZIP: {zip_path}...")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    # Mantener la estructura relativa dentro del ZIP
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)
        
        print(f"✅ ZIP creado: {zip_path}")
        
        # Subir a S3
        s3_key = f"{s3_prefix}/{lambda_name}.zip"
        s3_uri = f"s3://{bucket_name}/{s3_key}"
        print(f"📤 Subiendo a {s3_uri}...")
        
        result = subprocess.run(
            ["aws", "s3", "cp", str(zip_path), s3_uri, "--region", region],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {lambda_name} subido exitosamente")
            print(f"   Clave S3: {s3_key}")
            return s3_key
        else:
            raise RuntimeError(f"Error al subir {lambda_name} a S3: {result.stderr}")


def save_config(config_data, output_file="config.json"):
    """Guarda la configuración en un archivo JSON"""
    config_path = Path(output_file)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Configuración guardada en: {config_path.absolute()}")
    return config_path


def main():
    parser = argparse.ArgumentParser(
        description="Empaqueta y sube funciones Lambda a S3"
    )
    parser.add_argument(
        "--bucket-name",
        required=True,
        help="Nombre del bucket S3 donde se almacenarán los paquetes Lambda"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="Región de AWS (default: us-east-1)"
    )
    parser.add_argument(
        "--s3-prefix",
        default="lambdas",
        help="Prefijo para las claves S3 (default: lambdas)"
    )
    parser.add_argument(
        "--output-config",
        default="config.json",
        help="Nombre del archivo de configuración de salida (default: config.json)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Empaquetando y subiendo funciones Lambda a S3...")
    
    # Verificar AWS CLI
    if not check_aws_cli():
        sys.exit(1)
    
    # Verificar o crear bucket
    if not check_or_create_bucket(args.bucket_name, args.region):
        sys.exit(1)
    
    # Directorio base del proyecto
    project_root = Path(__file__).parent
    lambdas_dir = project_root / "lambdas"
    
    if not lambdas_dir.exists():
        print(f"❌ Error: No se encuentra el directorio 'lambdas' en {project_root}", file=sys.stderr)
        sys.exit(1)
    
    # Desplegar cada función Lambda
    lambda_configs = {}
    lambda_functions = ["connect", "disconnect", "default"]
    
    for lambda_name in lambda_functions:
        lambda_path = lambdas_dir / lambda_name
        if not lambda_path.exists():
            print(f"⚠️  Advertencia: No se encuentra {lambda_path}, saltando...")
            continue
        
        try:
            s3_key = deploy_lambda(
                lambda_name,
                str(lambda_path),
                args.bucket_name,
                args.s3_prefix,
                args.region
            )
            lambda_configs[lambda_name] = {
                "s3_key": s3_key,
                "s3_uri": f"s3://{args.bucket_name}/{s3_key}"
            }
        except Exception as e:
            print(f"❌ Error al desplegar {lambda_name}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Crear configuración
    config_data = {
        "bucket_name": args.bucket_name,
        "region": args.region,
        "s3_prefix": args.s3_prefix,
        "lambdas": lambda_configs,
        "cloudformation_parameters": {
            "S3BucketLambdaCode": args.bucket_name,
            "S3KeyConnectLambda": lambda_configs.get("connect", {}).get("s3_key", ""),
            "S3KeyDisconnectLambda": lambda_configs.get("disconnect", {}).get("s3_key", ""),
            "S3KeyDefaultLambda": lambda_configs.get("default", {}).get("s3_key", "")
        }
    }
    
    # Guardar configuración
    config_path = save_config(config_data, args.output_config)
    
    # Mostrar resumen
    print("\n✅ ¡Todas las funciones Lambda han sido desplegadas!")
    print("\n📋 Resumen de claves S3:")
    for lambda_name, config in lambda_configs.items():
        print(f"   - {lambda_name.capitalize():12} {config['s3_key']}")
    
    print(f"\n💡 Configuración guardada en: {config_path}")
    print("\n📝 Parámetros para CloudFormation:")
    for key, value in config_data["cloudformation_parameters"].items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
