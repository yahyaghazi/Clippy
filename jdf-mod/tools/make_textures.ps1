# Génère les textures 16x16 du mod à partir de "pixel maps" en texte.
# Chaque caractère = un pixel, '.' = transparent.
# Attention : les clés de hashtable PowerShell sont insensibles à la casse,
# donc chaque couleur doit avoir une lettre distincte même en ignorant la casse.
Add-Type -AssemblyName System.Drawing

function New-Texture {
    param([string]$Path, [string[]]$Rows, [hashtable]$Palette)

    if ($Rows.Count -ne 16) { throw "$Path : il faut 16 lignes, trouvé $($Rows.Count)" }
    $bmp = New-Object System.Drawing.Bitmap(16, 16)
    for ($y = 0; $y -lt 16; $y++) {
        if ($Rows[$y].Length -ne 16) { throw "$Path : ligne $y fait $($Rows[$y].Length) caractères au lieu de 16" }
        for ($x = 0; $x -lt 16; $x++) {
            $c = $Rows[$y][$x]
            if ($c -eq '.') {
                $color = [System.Drawing.Color]::FromArgb(0, 0, 0, 0)
            } else {
                $hex = $Palette[[string]$c]
                if (-not $hex) { throw "$Path : caractère inconnu '$c'" }
                $r = [Convert]::ToInt32($hex.Substring(1, 2), 16)
                $g = [Convert]::ToInt32($hex.Substring(3, 2), 16)
                $b = [Convert]::ToInt32($hex.Substring(5, 2), 16)
                $color = [System.Drawing.Color]::FromArgb(255, $r, $g, $b)
            }
            $bmp.SetPixel($x, $y, $color)
        }
    }
    $dir = Split-Path $Path -Parent
    New-Item -ItemType Directory -Force $dir | Out-Null
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Host "OK -> $Path"
}

$base = Join-Path $PSScriptRoot "..\src\main\resources\assets\jdf\textures"

# --- Ambre (goutte orange avec un moustique piégé) ---
New-Texture -Path "$base\item\amber.png" -Palette @{
    o = '#B35900'; A = '#FFAE33'; L = '#FFD97A'; D = '#E07B00'; m = '#4A3520'
} -Rows @(
    "................",
    "................",
    ".....oooo.......",
    "....oALLAo......",
    "...oALLAAAo.....",
    "..oALLAAAAAo....",
    "..oALAAAAAAo....",
    "..oAAAAmAAAo....",
    "..oAAAmmAAAo....",
    "..oAAAAAAADo....",
    "..oAAAAAADDo....",
    "...oAAAADDo.....",
    "....oAADDo......",
    ".....oooo.......",
    "................",
    "................"
)

# --- Seringue (verticale, liquide vert) ---
# k = gris foncé (contour), G = gris clair (métal), E = liquide vert, N = aiguille
New-Texture -Path "$base\item\syringe.png" -Palette @{
    N = '#D8D8D8'; k = '#6E6E6E'; G = '#C8C8C8'; E = '#59C93C'
} -Rows @(
    ".......N........",
    ".......N........",
    ".......N........",
    "......kkk.......",
    ".....kGGGk......",
    ".....kGEEk......",
    ".....kGEEk......",
    ".....kGEEk......",
    ".....kGEEk......",
    ".....kGEEk......",
    ".....kkkkk......",
    "......kGk.......",
    "......kGk.......",
    ".....kkkkk......",
    "....kGGGGGk.....",
    "................"
)

# --- Bloc de fossile (pierre avec ossements) ---
# S = pierre, d = pierre foncée, B = os, h = ombre d'os
New-Texture -Path "$base\block\fossil_block.png" -Palette @{
    S = '#9E9690'; d = '#7E7872'; B = '#E3DCC8'; h = '#BDB49A'
} -Rows @(
    "SSSdSSSSSSdSSSSS",
    "SdSSSSBBSSSSSdSS",
    "SSSSBBBBBBSSSSSS",
    "SSSBBhSShBBSdSSS",
    "SdSBhSSSShBSSSSS",
    "SSSBSSdSSSBBSSSS",
    "SSSSSSSSSShBSSdS",
    "SdSSSBBBSSSBSSSS",
    "SSSSBBhBBSSBSdSS",
    "SSdSBhShBBSBSSSS",
    "SSSSBSSShBBBSSSS",
    "SdSSSSdSShBSSSdS",
    "SSSSSdSSSSSSSSSS",
    "SSdSSSSSSdSSSdSS",
    "SSSSSSdSSSSSSSSS",
    "SSSdSSSSSdSSdSSS"
)
