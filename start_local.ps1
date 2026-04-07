$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Get-PythonCommand {
    $candidates = @(
        (Join-Path $repoRoot ".venv\Scripts\python.exe"),
        (Join-Path $repoRoot "..\tools\Python311\python.exe"),
        "python"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -eq "python") {
            $command = Get-Command python -ErrorAction SilentlyContinue
            if ($command) {
                return $command.Source
            }
            continue
        }

        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "没有找到可用的 Python。请先安装 Python，或在项目目录下准备 .venv。"
}

function Get-LanIpAddresses {
    $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254*" -and
            $_.IPAddress -notlike "198.18.*" -and
            $_.IPAddress -notlike "0.*"
        } |
        Sort-Object InterfaceMetric, SkipAsSource |
        Select-Object -ExpandProperty IPAddress -Unique

    return @($addresses)
}

$python = Get-PythonCommand
$port = if ($env:APP_PORT) { $env:APP_PORT } elseif ($env:PORT) { $env:PORT } else { "20000" }
$env:APP_PORT = $port

Write-Host ""
Write-Host "长篇连载工坊本地服务准备启动" -ForegroundColor Cyan
Write-Host "本机访问: http://127.0.0.1:$port" -ForegroundColor Green

$lanIps = Get-LanIpAddresses
if ($lanIps.Count -gt 0) {
    foreach ($ip in $lanIps) {
        Write-Host "局域网访问: http://$ip`:$port" -ForegroundColor Yellow
    }
    Write-Host "手机和电脑连同一个 Wi-Fi 时，手机浏览器直接打开上面的局域网地址即可。" -ForegroundColor Yellow
} else {
    Write-Host "没有识别到可用的局域网 IPv4 地址，手机可能暂时无法通过同网地址访问。" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "按 Ctrl+C 可停止服务。" -ForegroundColor DarkGray
Write-Host ""

& $python app.py
