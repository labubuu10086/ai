$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Get-PythonCommand {
    $candidates = @(
        (Join-Path $repoRoot "..\tools\Python311\python.exe"),
        (Join-Path $repoRoot ".venv\Scripts\python.exe"),
        "python"
    )

    $available = @()
    foreach ($candidate in $candidates) {
        if ($candidate -eq "python") {
            $command = Get-Command python -ErrorAction SilentlyContinue
            if ($command) {
                $available += $command.Source
            }
            continue
        }

        if (Test-Path $candidate) {
            $available += (Resolve-Path $candidate).Path
        }
    }

    foreach ($candidate in $available) {
        if (Test-PythonReady $candidate) {
            return $candidate
        }
    }

    if ($available.Count -gt 0) {
        return $available[0]
    }

    throw "No Python interpreter found. Install Python or create a .venv in this project."
}

function Test-PythonReady($pythonPath) {
    try {
        & $pythonPath -c "import flask, dotenv, requests, openai" 1>$null 2>$null
    } catch {
    }
    return ($LASTEXITCODE -eq 0)
}

function Ensure-PythonReady($pythonPath) {
    if (Test-PythonReady $pythonPath) {
        return
    }

    Write-Host "Installing missing dependencies..." -ForegroundColor Cyan
    & $pythonPath -m pip install -r (Join-Path $repoRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed."
    }
}

function Get-LanIpAddresses {
    $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.IPAddress -notlike "127.*") -and
            ($_.IPAddress -notlike "169.254*") -and
            ($_.IPAddress -notlike "198.18.*") -and
            ($_.IPAddress -notlike "0.*")
        } |
        Sort-Object InterfaceMetric, SkipAsSource |
        Select-Object -ExpandProperty IPAddress -Unique

    return @($addresses)
}

$python = Get-PythonCommand
Ensure-PythonReady $python
$port = if ($env:APP_PORT) { $env:APP_PORT } elseif ($env:PORT) { $env:PORT } else { "20000" }
$env:APP_PORT = $port

Write-Host ""
Write-Host "Local server is starting..." -ForegroundColor Cyan
Write-Host "Local URL: http://127.0.0.1:$port" -ForegroundColor Green

$lanIps = Get-LanIpAddresses
if ($lanIps.Count -gt 0) {
    foreach ($ip in $lanIps) {
        Write-Host "LAN URL:   http://$ip`:$port" -ForegroundColor Yellow
    }
    Write-Host "Use the LAN URL on your phone if the phone and this computer are on the same Wi-Fi." -ForegroundColor Yellow
} else {
    Write-Host "No usable LAN IPv4 address was detected." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor DarkGray
Write-Host ""

& $python app.py
exit $LASTEXITCODE
