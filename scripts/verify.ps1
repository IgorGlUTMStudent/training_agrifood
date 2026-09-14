$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\.."
try {
    python -m pytest backend/tests
    Push-Location frontend
    try {
        npm run build
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
