# Eltako2MQTT Documentation Index

Welcome to the Eltako2MQTT documentation! Find what you need below.

---

## 🚀 Quick Start

**New to Eltako2MQTT?** Start here:

1. **[Installation Guide](INSTALLATION.md)** - Step-by-step installation in Home Assistant
2. **[README.md](README.md)** - Overview and feature summary
3. **[MQTT Commands](MQTT_COMMANDS.md)** - How to control devices

---

## 📚 Documentation Guides

### For End Users

#### [README.md](README.md)
Main documentation with:
- Features and device types
- Quick installation overview
- Basic configuration
- Troubleshooting tips
- Home Assistant integration info

#### [INSTALLATION.md](INSTALLATION.md)
Detailed installation and configuration guide:
- System requirements
- Step-by-step installation
- Configuration explanation
- First steps after setup
- Comprehensive troubleshooting
- Common issues and solutions

#### [MQTT_COMMANDS.md](MQTT_COMMANDS.md)
Complete reference for device control:
- All device types and commands
- MQTT topic structure
- Examples for each device type
- Status topics and values
- Home Assistant automation examples
- Testing procedures

#### [RELEASE_NOTES.md](RELEASE_NOTES.md)
Comprehensive release notes for v1.1.0:
- Detailed feature descriptions
- Performance improvements
- Technical details
- Migration guide
- Installation instructions

#### [CHANGELOG.md](CHANGELOG.md)
Version history and technical changelog:
- All versions and changes
- Added features
- Bug fixes
- Breaking changes
- Detailed technical notes

### For Developers

#### [API.md](API.md)
Technical documentation for developers:
- Architecture overview
- Core classes and methods
- Data structures
- MiniSafe2 HTTP API details
- MQTT topics and payloads
- Async flow and event loops
- Error handling
- Logging system
- Performance considerations
- Extending the bridge

---

## 📖 Documentation by Topic

### Installation & Setup
- [Installation Guide](INSTALLATION.md) - Full step-by-step guide
- [README.md](README.md) - Quick installation overview

### Configuration
- [INSTALLATION.md](INSTALLATION.md#configuration) - Configuration options
- [README.md](README.md#configuration) - Configuration examples
- [API.md](API.md#data-structures) - Configuration object structure

### Usage & Control
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md) - All device commands
- [README.md](README.md#verwendung) - Usage overview
- [INSTALLATION.md](INSTALLATION.md#first-steps) - First steps guide

### Features (v1.1.0)
- [RELEASE_NOTES.md](RELEASE_NOTES.md#whats-new) - New features explained
- [CHANGELOG.md](CHANGELOG.md#added) - Feature list
- [README.md](README.md#was-ist-neu) - Feature overview

### Device Types
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md#device-types--commands) - All device types
- [README.md](README.md#about) - Supported devices
- [API.md](API.md#device-object) - Device data structure

### Home Assistant Integration
- [README.md](README.md#home-assistant-integration) - HA integration info
- [INSTALLATION.md](INSTALLATION.md#verify-home-assistant-integration) - Verification steps
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md#home-assistant-automation-examples) - Automation examples

### Troubleshooting
- [INSTALLATION.md](INSTALLATION.md#troubleshooting) - Main troubleshooting guide
- [README.md](README.md#support) - Support section
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md#troubleshooting-commands) - Testing commands
- [API.md](API.md#troubleshooting-guide) - Developer troubleshooting

### Technical Details
- [API.md](API.md) - Full technical documentation
- [CHANGELOG.md](CHANGELOG.md#technical-details) - Technical notes
- [RELEASE_NOTES.md](RELEASE_NOTES.md#technical-details) - Technical details

---

## 🎯 Quick Navigation

### "How do I...?"

**...install Eltako2MQTT?**  
→ [Installation Guide](INSTALLATION.md#installation)

**...configure it?**  
→ [Configuration Section](INSTALLATION.md#configuration)

**...control my blinds?**  
→ [Blinds Commands](MQTT_COMMANDS.md#-blinds--rollos)

**...dim my lights?**  
→ [Dimmer Commands](MQTT_COMMANDS.md#-dimmers)

**...turn on a switch?**  
→ [Switch Commands](MQTT_COMMANDS.md#-switches)

**...monitor my weather station?**  
→ [Weather Commands](MQTT_COMMANDS.md#-weather-stations)

**...set up automations?**  
→ [Automation Examples](MQTT_COMMANDS.md#home-assistant-automation-examples)

**...debug issues?**  
→ [Troubleshooting Guide](INSTALLATION.md#troubleshooting)

**...understand the code?**  
→ [API Documentation](API.md)

**...see what's new in v1.1.0?**  
→ [Release Notes](RELEASE_NOTES.md)

**...extend the bridge?**  
→ [Extending the Bridge](API.md#extending-the-bridge)

---

## 📋 Document Summary

| Document | Purpose | Audience | Length |
|----------|---------|----------|--------|
| [README.md](README.md) | Main overview and getting started | Everyone | Medium |
| [INSTALLATION.md](INSTALLATION.md) | Detailed setup and configuration | Users | Long |
| [MQTT_COMMANDS.md](MQTT_COMMANDS.md) | Device control reference | Users | Medium |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | v1.1.0 features and improvements | Users | Medium |
| [CHANGELOG.md](CHANGELOG.md) | Version history | Everyone | Short |
| [API.md](API.md) | Technical implementation | Developers | Long |
| [DOCUMENTATION.md](DOCUMENTATION.md) | This file | Everyone | Short |

---

## 🔄 Documentation Flow

### First Time Users
```
README.md
    ↓
INSTALLATION.md (Step 1-4: Install)
    ↓
INSTALLATION.md (Step 5: Verify)
    ↓
MQTT_COMMANDS.md (Learn to control)
```

### Troubleshooting
```
INSTALLATION.md (Troubleshooting section)
    ↓
API.md (Technical debugging)
    ↓
Issues on GitHub
```

### For Developers
```
README.md (Overview)
    ↓
API.md (Technical details)
    ↓
Source code: eltako2mqtt.py
```

---

## 🆘 Getting Help

### Quick Answers
1. Check relevant documentation (see above)
2. Search [INSTALLATION.md](INSTALLATION.md#troubleshooting) Troubleshooting section
3. Check [GitHub Issues](https://github.com/Olgrov/eltako2mqtt/issues)

### Report Issues
1. Collect debug info:
   - Set `logging.level` to `DEBUG`
   - Wait 2 minutes for logs
   - Copy relevant log entries
2. Check if issue already reported
3. Create new issue with:
   - Your Home Assistant version
   - Configuration (hide passwords)
   - Complete error logs
   - Steps to reproduce

### Get Support
- GitHub Issues: https://github.com/Olgrov/eltako2mqtt/issues
- Home Assistant Community: (if applicable)
- Check existing issues first!

---

## 📦 What's Included

### Code
- `eltako2mqtt.py` - Main bridge implementation
- `run.sh` - Docker/addon startup script
- `Dockerfile` - Multi-arch Docker container
- `config.yaml` - Configuration schema
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Main documentation
- `INSTALLATION.md` - Installation guide
- `MQTT_COMMANDS.md` - Command reference
- `RELEASE_NOTES.md` - Release information
- `CHANGELOG.md` - Version history
- `API.md` - Technical documentation
- `DOCUMENTATION.md` - This index (you are here)

---

## 🎓 Learning Path

### Beginner: "I just want it to work"
1. Read: [README.md](README.md) (5 min)
2. Follow: [INSTALLATION.md](INSTALLATION.md) installation steps (10 min)
3. Reference: [MQTT_COMMANDS.md](MQTT_COMMANDS.md) for control (as needed)

### Intermediate: "I want to understand it"
1. Read: Full [INSTALLATION.md](INSTALLATION.md) (15 min)
2. Learn: [MQTT_COMMANDS.md](MQTT_COMMANDS.md) (15 min)
3. Explore: [RELEASE_NOTES.md](RELEASE_NOTES.md) features (10 min)

### Advanced: "I want to extend/debug it"
1. Read: [API.md](API.md) architecture (20 min)
2. Review: Source code `eltako2mqtt.py`
3. Follow: [API.md](API.md#extending-the-bridge) extension guide

---

## 📞 Version Information

This documentation is for **Eltako2MQTT v1.1.0** and later.

**Key Features in v1.1.0:**
- ✨ Defensive brightness handling
- 🎯 Position-based blind control
- 📊 Smart hardware feedback logging
- ⏱️ Dynamic command timeout
- 🖥️ Configurable logging levels
- 🚀 Optimized polling (5s default)

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for complete details.

---

## 🤝 Contributing

Wants to improve documentation?
- Issues: https://github.com/Olgrov/eltako2mqtt/issues
- Pull Requests: https://github.com/Olgrov/eltako2mqtt/pulls

---

**Last Updated:** 2026-01-09  
**Version:** 1.1.0
