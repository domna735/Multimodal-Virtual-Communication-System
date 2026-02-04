param(
    [ValidateSet('auto','cpu','cuda','dml')]
    [string]$Device = 'dml',

    [ValidateSet('yunet','dnn','haar')]
    [string]$Detector = 'yunet',

    [switch]$Speak,

    [ValidateSet('offline','openai','azure-openai')]
    [string]$Llm = 'offline',

    [ValidateSet('windows','azure')]
    [string]$Tts = 'windows',

    [ValidateSet('off','azure')]
    [string]$Stt = 'off',

    [ValidateSet('push','continuous')]
    [string]$SttMode = 'push',

    [string]$SttLang = 'en-US',

    [ValidateSet('off','wav','mic')]
    [string]$Prosody = 'off',

    [string]$ProsodyWav = '',

    [double]$ProsodySeconds = 3.0
)

$ErrorActionPreference = 'Stop'

# Always run from this repo folder (works even if the path has spaces)
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$demo = Join-Path $PSScriptRoot 'demo\mvp_demo.py'

if (-not (Test-Path $python)) {
    throw "Python venv not found: $python`nCreate it first (see docs/mvp_demo_playbook.md)"
}

$cmd = @(
    $demo,
    '--device', $Device,
    '--detector', $Detector,
    '--llm', $Llm,
    '--tts', $Tts,
    '--stt', $Stt,
    '--stt-mode', $SttMode,
    '--stt-lang', $SttLang,
    '--prosody', $Prosody,
    '--prosody-seconds', "$ProsodySeconds"
)

if ($Prosody -eq 'wav') {
    if ([string]::IsNullOrWhiteSpace($ProsodyWav)) {
        throw "Prosody=wav requires -ProsodyWav <path-to-wav>"
    }
    $cmd += @('--prosody-wav', $ProsodyWav)
}

if ($Speak) {
    $cmd += '--speak'
}

& $python @cmd
