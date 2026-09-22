<#
Assembles a self-contained deployment package for the ingestion Function App
and zips it for Kudu Zip Deploy (no Azure CLI needed).

Usage:
    .\scripts\build_function_zip.ps1

Output:
    dist\ingestion_function.zip -- upload this at
    https://<your-function-app-name>.scm.azurewebsites.net/ZipDeployUI/
#>

$root = Split-Path -Parent $PSScriptRoot
$stagingDir = Join-Path $root "dist\ingestion_function"
$zipPath = Join-Path $root "dist\ingestion_function.zip"

if (Test-Path $stagingDir) { Remove-Item -Recurse -Force $stagingDir }
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null

# Function code
Copy-Item "$root\ingestion\function_app.py" $stagingDir
Copy-Item "$root\ingestion\ingest_pipeline.py" $stagingDir
Copy-Item "$root\ingestion\host.json" $stagingDir
Copy-Item "$root\ingestion\requirements.txt" $stagingDir

# Shared package, placed alongside function_app.py so `import siemens_wiki_common` resolves
Copy-Item "$root\shared\siemens_wiki_common" (Join-Path $stagingDir "siemens_wiki_common") -Recurse

# Sources config, at the relative path function_app.py expects (see SOURCES_PATH)
New-Item -ItemType Directory -Force -Path (Join-Path $stagingDir "config") | Out-Null
Copy-Item "$root\config\sources.yaml" (Join-Path $stagingDir "config\sources.yaml")

# Clean caches that don't belong in the deployment package
Get-ChildItem $stagingDir -Recurse -Include "__pycache__" -Directory | Remove-Item -Recurse -Force

Compress-Archive -Path "$stagingDir\*" -DestinationPath $zipPath -Force

Write-Output "Built $zipPath"
Write-Output "Upload it at: https://<your-function-app-name>.scm.azurewebsites.net/ZipDeployUI/"
