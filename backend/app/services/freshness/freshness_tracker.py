import datetime
from typing import Optional, Tuple
from backend.app.core.config import settings

class FreshnessTracker:
    @staticmethod
    def calculate_state(last_checked_at: Optional[datetime.datetime]) -> str:
        """
        Determines freshness state according to elapsed time.
        0-7 days = FRESH
        8-30 days = RECENT
        31+ days = STALE
        None = NEEDS_RECHECK
        """
        if not last_checked_at:
            return "NEEDS_RECHECK"
            
        now = datetime.datetime.now(datetime.timezone.utc) if (last_checked_at and last_checked_at.tzinfo) else datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        delta_days = (now - last_checked_at).days
        
        if delta_days <= settings.FRESHNESS_FRESH_DAYS:
            return "FRESH"
        elif delta_days <= settings.FRESHNESS_RECENT_DAYS:
            return "RECENT"
        else:
            return "STALE"

    @staticmethod
    def has_content_changed(old_hash: Optional[str], new_hash: Optional[str]) -> bool:
        if not old_hash or not new_hash:
            return False
        return old_hash.strip() != new_hash.strip()

freshness_tracker = FreshnessTracker()
