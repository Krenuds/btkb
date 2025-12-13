#include <Arduino.h>
#include <BleKeyboard.h>

// Initialize BLE Keyboard with device name, manufacturer, and battery level
BleKeyboard bleKeyboard("Bighead", "Bighead", 100);

// Buffer for incoming serial commands
String inputBuffer = "";
String originalBuffer = "";  // Preserve original case for TEXT command
const int MAX_BUFFER_SIZE = 256;

// Track connection state for automatic status reporting
bool wasConnected = false;

// Function declarations
void processCommand(String command);
void handleTextCommand(String text);
void handleKeyCommand(String keyName);
void handlePressCommand(String keyName);
void handleReleaseCommand(String keyName);
void handleMediaCommand(String action);
void handleStatusCommand();
uint8_t getKeyCode(String keyName);
const MediaKeyReport* getMediaKeyCode(String action);

void setup() {
    Serial.begin(115200);

    // Wait for serial to be ready
    while (!Serial) {
        delay(10);
    }

    Serial.println("Bighead Bluetooth Keyboard starting...");

    // Start BLE Keyboard
    bleKeyboard.begin();

    Serial.println("OK:READY");
    Serial.println("Waiting for Bluetooth connection...");
}

void loop() {
    // Check for connection state changes and report automatically
    bool isConnected = bleKeyboard.isConnected();
    if (isConnected != wasConnected) {
        wasConnected = isConnected;
        if (isConnected) {
            Serial.println("OK:CONNECTED");
        } else {
            Serial.println("OK:DISCONNECTED");
        }
    }

    // Read serial data
    while (Serial.available()) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            // Process command when newline received
            if (inputBuffer.length() > 0) {
                inputBuffer.trim();
                originalBuffer = inputBuffer;  // Save original case
                inputBuffer.toUpperCase();
                processCommand(inputBuffer);
                inputBuffer = "";
                originalBuffer = "";
            }
        } else {
            // Add character to buffer if not exceeding max size
            if (inputBuffer.length() < MAX_BUFFER_SIZE) {
                inputBuffer += c;
            }
        }
    }

    // Small delay to prevent watchdog issues
    delay(1);
}

void processCommand(String command) {
    // Check if connected before processing most commands
    if (command.startsWith("TEXT:")) {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        // Use originalBuffer to preserve case for text typing
        handleTextCommand(originalBuffer.substring(5));
    }
    else if (command.startsWith("KEY:")) {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        handleKeyCommand(command.substring(4));
    }
    else if (command.startsWith("PRESS:")) {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        handlePressCommand(command.substring(6));
    }
    else if (command.startsWith("RELEASE:")) {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        handleReleaseCommand(command.substring(8));
    }
    else if (command == "RELEASEALL") {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        bleKeyboard.releaseAll();
        Serial.println("OK:RELEASED");
    }
    else if (command.startsWith("MEDIA:")) {
        if (!bleKeyboard.isConnected()) {
            Serial.println("ERROR:NOT_CONNECTED");
            return;
        }
        handleMediaCommand(command.substring(6));
    }
    else if (command.startsWith("DELAY:")) {
        // DELAY can work even when not connected
        String delayStr = command.substring(6);
        int delayMs = delayStr.toInt();
        if (delayMs > 0 && delayMs <= 10000) {
            delay(delayMs);
            Serial.println("OK:DELAYED");
        } else {
            Serial.println("ERROR:INVALID_DELAY");
        }
    }
    else if (command == "STATUS") {
        handleStatusCommand();
    }
    else if (command.length() == 0) {
        // Ignore empty commands
    }
    else {
        Serial.println("ERROR:UNKNOWN_COMMAND");
    }
}

void handleTextCommand(String text) {
    bleKeyboard.print(text);
    Serial.println("OK:TYPED");
}

void handleKeyCommand(String keyName) {
    keyName.trim();
    uint8_t keyCode = getKeyCode(keyName);

    if (keyCode != 0) {
        bleKeyboard.write(keyCode);
        Serial.println("OK:KEY_SENT");
    } else {
        Serial.println("ERROR:INVALID_KEYCODE");
    }
}

void handlePressCommand(String keyName) {
    keyName.trim();
    uint8_t keyCode = getKeyCode(keyName);

    if (keyCode != 0) {
        bleKeyboard.press(keyCode);
        Serial.println("OK:KEY_PRESSED");
    } else {
        Serial.println("ERROR:INVALID_KEYCODE");
    }
}

void handleReleaseCommand(String keyName) {
    keyName.trim();
    uint8_t keyCode = getKeyCode(keyName);

    if (keyCode != 0) {
        bleKeyboard.release(keyCode);
        Serial.println("OK:KEY_RELEASED");
    } else {
        Serial.println("ERROR:INVALID_KEYCODE");
    }
}

void handleMediaCommand(String action) {
    action.trim();
    const MediaKeyReport* mediaKey = getMediaKeyCode(action);

    if (mediaKey != nullptr) {
        bleKeyboard.write(*mediaKey);
        Serial.println("OK:MEDIA_SENT");
    } else {
        Serial.println("ERROR:INVALID_MEDIA_KEY");
    }
}

void handleStatusCommand() {
    if (bleKeyboard.isConnected()) {
        Serial.println("OK:CONNECTED");
    } else {
        Serial.println("OK:DISCONNECTED");
    }
}

uint8_t getKeyCode(String keyName) {
    // Basic keys
    if (keyName == "ENTER" || keyName == "RETURN") return KEY_RETURN;
    if (keyName == "TAB") return KEY_TAB;
    if (keyName == "SPACE") return ' ';
    if (keyName == "BACKSPACE" || keyName == "BKSP") return KEY_BACKSPACE;
    if (keyName == "DELETE" || keyName == "DEL") return KEY_DELETE;
    if (keyName == "ESC" || keyName == "ESCAPE") return KEY_ESC;

    // Arrow keys
    if (keyName == "UP") return KEY_UP_ARROW;
    if (keyName == "DOWN") return KEY_DOWN_ARROW;
    if (keyName == "LEFT") return KEY_LEFT_ARROW;
    if (keyName == "RIGHT") return KEY_RIGHT_ARROW;

    // Modifiers
    if (keyName == "CTRL" || keyName == "CONTROL") return KEY_LEFT_CTRL;
    if (keyName == "SHIFT") return KEY_LEFT_SHIFT;
    if (keyName == "ALT") return KEY_LEFT_ALT;
    if (keyName == "GUI" || keyName == "WIN" || keyName == "WINDOWS" || keyName == "META") return KEY_LEFT_GUI;

    // Right-side modifiers
    if (keyName == "RCTRL") return KEY_RIGHT_CTRL;
    if (keyName == "RSHIFT") return KEY_RIGHT_SHIFT;
    if (keyName == "RALT") return KEY_RIGHT_ALT;
    if (keyName == "RGUI") return KEY_RIGHT_GUI;

    // Function keys
    if (keyName == "F1") return KEY_F1;
    if (keyName == "F2") return KEY_F2;
    if (keyName == "F3") return KEY_F3;
    if (keyName == "F4") return KEY_F4;
    if (keyName == "F5") return KEY_F5;
    if (keyName == "F6") return KEY_F6;
    if (keyName == "F7") return KEY_F7;
    if (keyName == "F8") return KEY_F8;
    if (keyName == "F9") return KEY_F9;
    if (keyName == "F10") return KEY_F10;
    if (keyName == "F11") return KEY_F11;
    if (keyName == "F12") return KEY_F12;

    // Navigation keys
    if (keyName == "HOME") return KEY_HOME;
    if (keyName == "END") return KEY_END;
    if (keyName == "PAGEUP" || keyName == "PGUP") return KEY_PAGE_UP;
    if (keyName == "PAGEDOWN" || keyName == "PGDN") return KEY_PAGE_DOWN;
    if (keyName == "INSERT" || keyName == "INS") return KEY_INSERT;

    // Special keys
    if (keyName == "CAPSLOCK" || keyName == "CAPS") return KEY_CAPS_LOCK;
    if (keyName == "PRINTSCREEN" || keyName == "PRTSC") return KEY_PRTSC;

    // Single character keys (A-Z, 0-9)
    if (keyName.length() == 1) {
        char c = keyName.charAt(0);
        if (c >= 'A' && c <= 'Z') {
            return c - 'A' + 'a';  // Return lowercase
        }
        if (c >= '0' && c <= '9') {
            return c;
        }
    }

    return 0;  // Invalid key
}

const MediaKeyReport* getMediaKeyCode(String action) {
    if (action == "PLAY" || action == "PAUSE" || action == "PLAYPAUSE") return &KEY_MEDIA_PLAY_PAUSE;
    if (action == "STOP") return &KEY_MEDIA_STOP;
    if (action == "NEXT" || action == "NEXTTRACK") return &KEY_MEDIA_NEXT_TRACK;
    if (action == "PREV" || action == "PREVIOUS" || action == "PREVTRACK") return &KEY_MEDIA_PREVIOUS_TRACK;
    if (action == "VOLUMEUP" || action == "VOLUP") return &KEY_MEDIA_VOLUME_UP;
    if (action == "VOLUMEDOWN" || action == "VOLDOWN") return &KEY_MEDIA_VOLUME_DOWN;
    if (action == "MUTE") return &KEY_MEDIA_MUTE;

    return nullptr;  // Invalid media key
}
