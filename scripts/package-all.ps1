$ErrorActionPreference = "Stop"

$ORIGINAL_DIR = Get-Location

try {
    # Directorio del script
    $SCRIPT_DIR = $PSScriptRoot

    # Root real del proyecto
    $ROOT_DIR = Resolve-Path (Join-Path $SCRIPT_DIR "..\apiRest")


    Set-Location $ROOT_DIR

    ### ================================
    ### CONFIGURACIÓN (root: apiRest/)
    ### ================================

    $UPLOAD_DIR   = Join-Path $ROOT_DIR "../upload_aws"
    $LAYER_DIR    = Join-Path $ROOT_DIR "layer"
    $DOMAIN_DIR   = Join-Path $ROOT_DIR "packages/domain"
    $DOMAIN_ENTRY = Join-Path $DOMAIN_DIR "src/index.ts"
    $LAMBDAS_DIR  = Join-Path $ROOT_DIR "lambdas"

    ### ================================
    ### PREP: carpeta upload_aws
    ### ================================
    Write-Host "📂 Preparando carpeta upload_aws..."
    if (Test-Path $UPLOAD_DIR) {
        Remove-Item -Recurse -Force $UPLOAD_DIR
    }
    New-Item -ItemType Directory -Force -Path $UPLOAD_DIR | Out-Null


    ### ================================
    ### 1️⃣ LIMPIEZA INICIAL
    ### ================================
    Write-Host "🧹 Limpieza inicial..."

    @(
        $LAYER_DIR,
        "$DOMAIN_DIR/node_modules",
        "$DOMAIN_DIR/dist"
    ) | ForEach-Object {
        if (Test-Path $_) {
            Remove-Item -Recurse -Force $_
        }
    }

    Get-ChildItem $LAMBDAS_DIR -Directory | ForEach-Object {

        $lambdaDir = $_.FullName

        @("node_modules", "dist", "package") | ForEach-Object {
            $p = Join-Path $lambdaDir $_
            if (Test-Path $p) {
                Remove-Item -Recurse -Force $p
            }
        }
    }


    ### ================================
    ### 2️⃣ DOMAIN: npm install
    ### ================================
    Write-Host "📦 Instalando dependencias del domain..."
    npm install --prefix $DOMAIN_DIR --silent


    ### ================================
    ### 3️⃣ DOMAIN: tsc
    ### ================================
    Write-Host "🧠 Compilando domain (tsc)..."
    Push-Location $DOMAIN_DIR
    npx tsc --pretty false
    Pop-Location


    ### ================================
    ### 4️⃣ DOMAIN: esbuild → Lambda Layer
    ### ================================
    Write-Host "📦 Generando Lambda Layer..."

    $layerPackagePath = "$LAYER_DIR/nodejs/node_modules/@game/domain"
    New-Item -ItemType Directory -Force -Path $layerPackagePath | Out-Null

    npx esbuild $DOMAIN_ENTRY `
    --bundle `
    --platform=node `
    --target=node18 `
    --outfile="$layerPackagePath/index.js" `
    --external:@aws-sdk/* `
    --minify `
    --sourcemap `
    --log-level=error


    ### ================================
    ### 5️⃣ ZIP LAYER
    ### ================================
    Write-Host "📦 Empaquetando Lambda Layer..."

    $layerZipPath = Join-Path $UPLOAD_DIR "domain-layer.zip"

    if (Test-Path $layerZipPath) {
        Remove-Item $layerZipPath -Force
    }

    $layerFiles = Get-ChildItem -Path $LAYER_DIR -Recurse

    Compress-Archive `
        -Path $layerFiles.FullName `
        -DestinationPath $layerZipPath


    ### ================================
    ### 6️⃣ LAMBDAS: npm install + tsc
    ### ================================
    Write-Host "🧠 Build de Lambdas..."

    Get-ChildItem $LAMBDAS_DIR -Directory | ForEach-Object {

        Write-Host "   → $($_.Name)"

        npm install --prefix $_.FullName --silent

        Push-Location $_.FullName
        npx tsc --pretty false
        Pop-Location
    }


    ### ================================
    ### 7️⃣ ZIP LAMBDAS
    ### ================================
    Write-Host "🚀 Empaquetando Lambdas..."

    Get-ChildItem $LAMBDAS_DIR -Directory | ForEach-Object {

        $lambdaName = $_.Name
        $distDir    = Join-Path $_.FullName "dist"
        $zipPath    = Join-Path $UPLOAD_DIR "$lambdaName.zip"

        if (!(Test-Path $distDir)) {
            Write-Host "   ⏭️  $lambdaName sin dist/, se omite"
            return
        }

        Write-Host "   → $lambdaName"

        if (Test-Path $zipPath) {
            Remove-Item $zipPath
        }

        Push-Location $distDir
        Compress-Archive -Path * -DestinationPath $zipPath
        Pop-Location
    }


    ### ================================
    ### 8️⃣ LIMPIEZA FINAL
    ### ================================
    Write-Host "🧹 Limpieza final..."

    # Domain
    @(
        (Join-Path $DOMAIN_DIR "node_modules"),
        (Join-Path $DOMAIN_DIR "dist"),
        (Join-Path $DOMAIN_DIR "package-lock.json")
    ) | ForEach-Object {
        if (Test-Path $_) {
            Remove-Item -Recurse -Force $_
        }
    }

    # Lambdas
    Get-ChildItem $LAMBDAS_DIR -Directory | ForEach-Object {
        @(
            (Join-Path $_.FullName "node_modules"),
            (Join-Path $_.FullName "dist"),
            (Join-Path $_.FullName "package-lock.json"),
            (Join-Path $_.FullName "package")
        ) | ForEach-Object {
            if (Test-Path $_) {
                Remove-Item -Recurse -Force $_
            }
        }
    }

    # Layer sin zip
    if (Test-Path $LAYER_DIR) {
        Remove-Item -Recurse -Force $LAYER_DIR
    }

    Write-Host "🎉 Build completo. Zips listos en upload_aws/"
}
finally {
    Set-Location $ORIGINAL_DIR
}