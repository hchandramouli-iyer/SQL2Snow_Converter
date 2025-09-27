# 🪟 CodeCraft AI Windows Desktop App - Complete Guide

## ✅ YES! Windows Executable WITHOUT Admin Rights

**Your CodeCraft AI desktop app can run on Windows machines WITHOUT requiring admin privileges!**

## 🎯 Build Options for Windows

We're creating **3 different Windows distributions**:

### 1. **Portable Executable** ⭐ (RECOMMENDED for No-Admin)
- **File**: `CodeCraft AI-1.0.0-win.exe` (portable)
- **Size**: ~200MB
- **Installation**: None required
- **Admin Rights**: ❌ Not needed
- **Usage**: Double-click to run instantly
- **Perfect for**: Corporate environments, restricted machines

### 2. **User-Level Installer**
- **File**: `CodeCraft AI Setup-1.0.0.exe` (installer)
- **Installation**: Installs to user's AppData folder
- **Admin Rights**: ❌ Not needed
- **Features**: Start menu shortcuts, desktop icon
- **Perfect for**: Personal machines, permanent installation

### 3. **ZIP Package**
- **File**: `CodeCraft AI-1.0.0-win.zip`
- **Installation**: Extract and run
- **Admin Rights**: ❌ Not needed
- **Usage**: Extract, then run `CodeCraft AI.exe`
- **Perfect for**: IT deployment, manual distribution

## 🔧 How to Build Windows Version

### Method 1: Quick Build
```bash
cd /app/frontend
yarn dist-win
```

### Method 2: Using Our Script
```bash
cd /app/frontend
./build-windows.sh
```

### Method 3: Specific Targets
```bash
# Portable only
yarn electron-builder --win --target portable

# Installer only  
yarn electron-builder --win --target nsis

# ZIP only
yarn electron-builder --win --target zip
```

## 📋 Configuration Details

Our build is configured with:
- ✅ **No Admin Rights Required** (`requestedExecutionLevel: "asInvoker"`)
- ✅ **User-Level Installation** (`perMachine: false`)
- ✅ **No Elevation Prompts** (`allowElevation: false`)
- ✅ **Both 64-bit and 32-bit** support
- ✅ **Code Signing Disabled** (no certificates needed)

## 🚀 Distribution Instructions

### For IT Departments:
1. **Download** the portable .exe file
2. **Copy** to network share or USB drives
3. **Users** can run directly from any location
4. **No installation** or admin rights needed

### For End Users:
1. **Download** the installer or portable version
2. **Run** the executable
3. **Use** immediately - no setup required

## 📁 File Locations (No Admin Install)

When installed without admin rights:
- **Program Files**: `%LOCALAPPDATA%\Programs\CodeCraft AI\`
- **User Data**: `%APPDATA%\codecraft-ai-desktop\`
- **Shortcuts**: Desktop and Start Menu (user-level only)

## 🔒 Security & Corporate Compliance

### Security Features:
- ✅ **Sandboxed Execution** (Chromium security model)
- ✅ **No System Modifications** (user-space only)
- ✅ **No Registry Changes** (portable mode)
- ✅ **No Service Installation** (desktop app only)

### Corporate Environment Ready:
- ✅ **No Admin Rights** required
- ✅ **Portable Execution** possible
- ✅ **Network Share Compatible**
- ✅ **Group Policy Friendly**
- ✅ **Antivirus Scannable**

## 💾 System Requirements

**Minimum Requirements:**
- Windows 10 (64-bit or 32-bit)
- 4GB RAM
- 500MB disk space
- No special permissions

**Recommended:**
- Windows 10/11 (64-bit)
- 8GB RAM
- 1GB disk space
- Internet connection (for AI features with backend)

## 🎯 Current Build Status

Building Windows executables now! The process creates:
1. **win-unpacked/** - Development version
2. **CodeCraft AI-1.0.0-win.exe** - Portable executable
3. **CodeCraft AI Setup-1.0.0.exe** - User installer
4. **CodeCraft AI-1.0.0-win.zip** - ZIP package

## 🏃‍♂️ Quick Start for Windows

Once built, users can:
1. **Download** the portable .exe
2. **Save** to any folder (Desktop, USB, Network drive)
3. **Double-click** to run
4. **Use** immediately - all features available!

## 🔄 Updates & Maintenance

- **Auto-updater** ready (optional)
- **Manual updates** by replacing executable
- **Settings preserved** between versions
- **No uninstaller needed** (just delete files)

**Perfect for corporate environments where admin rights are restricted!** 🎉