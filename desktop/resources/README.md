# Ottoman Agent Desktop - Build Resources

This directory contains icons and resources for desktop builds.

## Icon Requirements

### Windows (icon.ico)
- Format: ICO
- Sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- Create with: https://www.ionicon.com or convert from PNG

### macOS (icon.icns)
- Format: ICNS
- Source: PNG 1024x1024
- Create with: https://www.iconconverter.com

### Linux (icon.png)
- Format: PNG
- Sizes: 32x32, 48x48, 64x64, 128x128, 256x256
- Create with: https://www.ionicon.com

## Creating Icons

### Option 1: Online Converter
1. Go to https://www.ionicon.com
2. Upload a high-res PNG (1024x1024 minimum)
3. Download all formats

### Option 2: Command Line (Linux/Mac)
```bash
# Convert PNG to ICO (Windows)
convert icon.png -define icon:auto-resize=16,32,48,64,128,256 icon.ico

# Convert PNG to ICNS (macOS)
iconutil -c icns icon.iconset
mkdir -p icon.iconset
sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
# ... (repeat for other sizes)
```

### Option 3: Python Script
```python
from PIL import Image
import os

def create_icons():
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create ICO for Windows
    images = []
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        images.append(img)
    
    images[0].save('resources/icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    
    # Create ICNS for macOS
    iconset_dir = 'resources/icon.iconset'
    os.makedirs(iconset_dir, exist_ok=True)
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        img.save(f'{iconset_dir}/icon_{size}x{size}.png')
        if size >= 128:
            img.save(f'{iconset_dir}/icon_{size}x{size}@2x.png')
    
    print("Icons created successfully!")

if __name__ == '__main__':
    create_icons()
```

## Current Status

- [x] Package configuration updated
- [ ] Icon files need to be created (see above)
- [ ] Test build: `npm run build:win`

## Build Commands

```bash
# Install dependencies
npm install

# Development mode
npm start

# Build for Windows
npm run build:win

# Build for macOS
npm run build:mac

# Build for Linux
npm run build:linux
```
