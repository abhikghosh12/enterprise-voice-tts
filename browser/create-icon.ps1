# PowerShell script to create a basic icon from SVG
# This creates a 256x256 PNG that electron-builder can use

Write-Host "Creating icon for Windows installer..." -ForegroundColor Cyan

# Check if ImageMagick is available (optional)
$magickPath = Get-Command magick -ErrorAction SilentlyContinue

if ($magickPath) {
    Write-Host "Found ImageMagick, converting SVG to PNG..." -ForegroundColor Green
    magick convert -background none -size 256x256 icon.svg icon.png
    Write-Host "Icon created: icon.png" -ForegroundColor Green
} else {
    Write-Host "ImageMagick not found. You can:" -ForegroundColor Yellow
    Write-Host "1. Install ImageMagick: winget install ImageMagick.ImageMagick" -ForegroundColor Yellow
    Write-Host "2. Or manually create icon.png (256x256 recommended)" -ForegroundColor Yellow
    Write-Host "3. Or use the provided icon creation guide below" -ForegroundColor Yellow

    Write-Host "`nFor now, creating a placeholder..." -ForegroundColor Cyan

    # Create a simple colored square as placeholder
    # This requires .NET which is usually available on Windows
    Add-Type -AssemblyName System.Drawing

    $bmp = New-Object System.Drawing.Bitmap(256, 256)
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)

    # Fill with gradient blue background
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        [System.Drawing.Point]::new(0, 0),
        [System.Drawing.Point]::new(256, 256),
        [System.Drawing.Color]::FromArgb(0, 120, 212),
        [System.Drawing.Color]::FromArgb(0, 90, 158)
    )
    $graphics.FillRectangle($brush, 0, 0, 256, 256)

    # Add text
    $font = New-Object System.Drawing.Font("Segoe UI", 48, [System.Drawing.FontStyle]::Bold)
    $textBrush = [System.Drawing.Brushes]::White
    $text = "EVB"
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center

    $graphics.DrawString($text, $font, $textBrush, 128, 128, $format)

    # Save
    $bmp.Save("icon.png", [System.Drawing.Imaging.ImageFormat]::Png)

    # Cleanup
    $graphics.Dispose()
    $bmp.Dispose()
    $brush.Dispose()
    $font.Dispose()

    Write-Host "Created placeholder icon: icon.png" -ForegroundColor Green
}

Write-Host "`nIcon ready for building!" -ForegroundColor Green
