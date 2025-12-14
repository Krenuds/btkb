"""
Keyword Matcher for STT-triggered emotes.

Maps spoken keywords to emote pools with cooldown management.
"""

import random
import time
from typing import Optional


class KeywordMatcher:
    """
    Matches transcribed text against keyword triggers.

    Supports many-to-many mapping:
    - Multiple trigger words can map to the same emote pool
    - Each trigger group has independent cooldown tracking
    """

    def __init__(self, config: dict):
        """
        Initialize the keyword matcher.

        Args:
            config: keyword_triggers config dict with keys:
                - cooldown: Seconds between triggers for same group
                - groups: List of {triggers: [...], emotes: [...]}
        """
        self.cooldown = config.get("cooldown", 3.0)
        groups = config.get("groups", [])

        # Build lookup: word -> (group_index, emotes_list)
        self._trigger_map = {}
        self._group_emotes = []

        for idx, group in enumerate(groups):
            triggers = group.get("triggers", [])
            emotes = group.get("emotes", [])
            self._group_emotes.append(emotes)

            for trigger in triggers:
                # Normalize to lowercase
                self._trigger_map[trigger.lower()] = idx

        # Track last trigger time per group
        self._last_trigger = {}

    def match(self, text: str) -> Optional[str]:
        """
        Check text for keyword triggers.

        Args:
            text: Transcribed text to scan

        Returns:
            Emote name if triggered, None otherwise
        """
        now = time.time()
        text_lower = text.lower()

        # Scan each word for triggers
        for word in text_lower.split():
            # Strip punctuation
            word = word.strip(".,!?\"'")

            if word in self._trigger_map:
                group_idx = self._trigger_map[word]

                # Check cooldown
                last_time = self._last_trigger.get(group_idx, 0)
                if (now - last_time) >= self.cooldown:
                    # Cooldown elapsed, trigger emote
                    self._last_trigger[group_idx] = now
                    emotes = self._group_emotes[group_idx]
                    if emotes:
                        emote = random.choice(emotes)
                        return emote

        return None
