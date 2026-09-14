$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\.."
try {
    $repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -Path $python -PathType Leaf)) {
        $unixPython = Join-Path $repoRoot ".venv/bin/python"
        if (Test-Path -Path $unixPython -PathType Leaf) {
            $python = $unixPython
        }
    }

    if (-not (Test-Path -Path $python -PathType Leaf)) {
        Write-Error "Project Python environment not found at '$python'. Please set up .venv as documented in README.md."
        exit 1
    }

    & $python -m pytest backend/tests
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Push-Location frontend
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}

