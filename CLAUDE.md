# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PlatformIO-based ESP32 project targeting the ESP-WROOM-32 development board using the Arduino framework.

## Build and Development Commands

**Build the project:**
```bash
pio run
```

**Upload to ESP32:**
```bash
pio run --target upload
```

**Serial monitor:**
```bash
pio device monitor
```

**Build, upload, and monitor (combined):**
```bash
pio run --target upload && pio device monitor
```

**Clean build files:**
```bash
pio run --target clean
```

**Run tests:**
```bash
pio test
```

## Configuration

- **Board:** ESP32 Dev Module (ESP-WROOM-32)
- **Upload speed:** 921600 baud
- **Serial monitor speed:** 115200 baud (ensure `Serial.begin(115200)` matches this)
- **Framework:** Arduino

When adding Serial communication, always initialize with `Serial.begin(115200)` in the `setup()` function to match the monitor_speed in platformio.ini:20.

## Project Structure

- `src/main.cpp` - Main application entry point with `setup()` and `loop()` functions
- `include/` - Header files for the project
- `lib/` - Project-specific libraries
- `test/` - Unit tests
- `.pio/` - PlatformIO build artifacts (gitignored)


