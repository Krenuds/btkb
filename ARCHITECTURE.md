# Architecture

## System Overview

```mermaid
flowchart TB
    subgraph Input
        MIC[Microphone]
    end

    subgraph Processing
        AUDIO[Audio Capture<br/>PyAudio]
        VAD[VAD<br/>Silero]
        STT[Keyword Matcher<br/>Whisper STT]
        SM[State Machine<br/>IDLE / TALKING]
    end

    subgraph Output
        DRIVER[FiveMDriver<br/>clipboard]
        ESP[ESP32 BLE<br/>Keyboard]
        FIVEM[FiveM]
    end

    MIC --> AUDIO
    AUDIO --> VAD
    AUDIO --> STT

    VAD -->|speech start<br/>speech end| SM
    STT -->|keyword emote| SM

    SM -->|emote command| DRIVER
    DRIVER -->|serial| ESP
    ESP -->|BLE HID| FIVEM
```

## Data Flow

1. **Audio Capture**: PyAudio captures microphone input in real-time
2. **Dual Processing**: Audio is processed by both VAD and STT simultaneously
   - **VAD (Silero)**: Detects speech start/end events
   - **STT (Whisper)**: Transcribes speech and matches keywords
3. **State Machine**: Receives events from both processors and decides which emote to trigger
4. **Output Chain**: Emote commands flow through FiveMDriver → ESP32 → FiveM

## State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE

    IDLE --> TALKING: speech_start
    TALKING --> IDLE: speech_end

    TALKING --> TALKING: timer (4s) → random emote
    TALKING --> TALKING: keyword → keyword emote

    IDLE --> TALKING: keyword detected

    note right of TALKING
        While talking:
        - Random emotes cycle every 4s
        - Keywords take priority
    end note

    note right of IDLE
        On speech end:
        - Play idle_emote (optional)
        - Return to IDLE state
    end note
```

## Component Responsibilities

```mermaid
flowchart LR
    subgraph Python
        main[main.py<br/>Orchestrator]
        vad[vad.py<br/>Voice Activity]
        stt[stt.py<br/>Speech-to-Text]
        kw[keyword_matcher.py<br/>Trigger Matching]
        sm[state_machine.py<br/>State Control]
        driver[fivem_driver.py<br/>Command Output]
        bh[bighead.py<br/>Serial Comms]
    end

    subgraph ESP32
        fw[main.cpp<br/>BLE Keyboard]
    end

    main --> vad
    main --> stt
    stt --> kw
    main --> sm
    sm --> driver
    driver --> bh
    bh -->|Serial| fw
```

## Emote Priority

```mermaid
flowchart TD
    EVENT[Event Received]

    EVENT --> KW{Keyword<br/>Detected?}
    KW -->|Yes| KWEMOTE[Play Keyword Emote<br/>Reset Timer]
    KW -->|No| TIMER{Timer<br/>Expired?}

    TIMER -->|Yes| RANDOM[Play Random Emote<br/>Reset Timer]
    TIMER -->|No| WAIT[Wait]

    KWEMOTE --> CONTINUE[Continue in TALKING]
    RANDOM --> CONTINUE
    WAIT --> CONTINUE
```
