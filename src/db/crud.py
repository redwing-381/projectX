"""CRUD operations for database models."""

from datetime import datetime, date
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.db.models import AlertHistory, VIPSender, KeywordRule, Settings


# =============================================================================
# Alert History Operations
# =============================================================================

def create_alert(
    db: Session,
    email_id: str,
    sender: str,
    subject: str,
    snippet: str,
    urgency: str,
    reason: str,
    sms_sent: bool = False,
    source: str = "email",
) -> AlertHistory:
    """Create a new alert history record."""
    alert = AlertHistory(
        email_id=email_id,
        sender=sender,
        subject=subject,
        snippet=snippet,
        urgency=urgency,
        reason=reason,
        sms_sent=sms_sent,
        source=source,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alert_by_email_id(db: Session, email_id: str) -> Optional[AlertHistory]:
    """Get alert by email ID."""
    return db.query(AlertHistory).filter(AlertHistory.email_id == email_id).first()


def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    urgency: Optional[str] = None,
    search: Optional[str] = None,
) -> List[AlertHistory]:
    """Get paginated list of alerts with optional filters."""
    query = db.query(AlertHistory)
    
    if urgency:
        query = query.filter(AlertHistory.urgency == urgency)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                AlertHistory.sender.ilike(search_term),
                AlertHistory.subject.ilike(search_term),
            )
        )
    
    return query.order_by(AlertHistory.created_at.desc()).offset(skip).limit(limit).all()


def get_alerts_count(
    db: Session,
    urgency: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    """Get total count of alerts with optional filters."""
    query = db.query(func.count(AlertHistory.id))
    
    if urgency:
        query = query.filter(AlertHistory.urgency == urgency)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                AlertHistory.sender.ilike(search_term),
                AlertHistory.subject.ilike(search_term),
            )
        )
    
    return query.scalar() or 0



def get_today_stats(db: Session) -> dict:
    """Get statistics for today."""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    
    total_today = db.query(func.count(AlertHistory.id)).filter(
        AlertHistory.created_at >= today_start
    ).scalar() or 0
    
    alerts_today = db.query(func.count(AlertHistory.id)).filter(
        AlertHistory.created_at >= today_start,
        AlertHistory.urgency == "URGENT",
        AlertHistory.sms_sent == True,
    ).scalar() or 0
    
    return {
        "emails_checked": total_today,
        "alerts_sent": alerts_today,
    }


def get_recent_alerts(db: Session, limit: int = 5) -> List[AlertHistory]:
    """Get most recent alerts."""
    return db.query(AlertHistory).order_by(
        AlertHistory.created_at.desc()
    ).limit(limit).all()


# =============================================================================
# VIP Sender Operations
# =============================================================================

def get_vip_senders(db: Session) -> List[VIPSender]:
    """Get all VIP senders."""
    return db.query(VIPSender).order_by(VIPSender.created_at.desc()).all()


def add_vip_sender(db: Session, email_or_domain: str) -> VIPSender:
    """Add a new VIP sender."""
    vip = VIPSender(email_or_domain=email_or_domain.lower().strip())
    db.add(vip)
    db.commit()
    db.refresh(vip)
    return vip


def remove_vip_sender(db: Session, id: int) -> bool:
    """Remove a VIP sender by ID."""
    vip = db.query(VIPSender).filter(VIPSender.id == id).first()
    if vip:
        db.delete(vip)
        db.commit()
        return True
    return False


def is_vip_sender(db: Session, email: str) -> Tuple[bool, Optional[str]]:
    """Check if email matches any VIP sender.
    
    Returns:
        Tuple of (is_vip, matched_rule)
    """
    email_lower = email.lower()
    vip_senders = db.query(VIPSender).all()
    
    for vip in vip_senders:
        rule = vip.email_or_domain.lower()
        # Check exact match or domain match
        if rule in email_lower or email_lower.endswith(f"@{rule}") or email_lower.endswith(f".{rule}"):
            return True, vip.email_or_domain
    
    return False, None


# =============================================================================
# Keyword Rule Operations
# =============================================================================

def get_keywords(db: Session) -> List[KeywordRule]:
    """Get all keyword rules."""
    return db.query(KeywordRule).order_by(KeywordRule.created_at.desc()).all()


def add_keyword(db: Session, keyword: str) -> KeywordRule:
    """Add a new keyword rule."""
    rule = KeywordRule(keyword=keyword.lower().strip())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def remove_keyword(db: Session, id: int) -> bool:
    """Remove a keyword rule by ID."""
    rule = db.query(KeywordRule).filter(KeywordRule.id == id).first()
    if rule:
        db.delete(rule)
        db.commit()
        return True
    return False


def has_urgent_keyword(db: Session, text: str) -> Tuple[bool, Optional[str]]:
    """Check if text contains any urgent keyword.
    
    Returns:
        Tuple of (has_keyword, matched_keyword)
    """
    text_lower = text.lower()
    keywords = db.query(KeywordRule).all()
    
    for kw in keywords:
        if kw.keyword.lower() in text_lower:
            return True, kw.keyword
    
    return False, None


# =============================================================================
# Settings Operations
# =============================================================================

def get_setting(db: Session, key: str, default: str = "") -> str:
    """Get a setting value by key."""
    setting = db.query(Settings).filter(Settings.key == key).first()
    return setting.value if setting else default


def set_setting(db: Session, key: str, value: str) -> Settings:
    """Set a setting value."""
    setting = db.query(Settings).filter(Settings.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Settings(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def get_all_settings(db: Session) -> dict:
    """Get all settings as a dictionary."""
    settings = db.query(Settings).all()
    return {s.key: s.value for s in settings}


# =============================================================================
# Monitoring Settings Operations
# =============================================================================

def get_monitoring_enabled(db: Session) -> bool:
    """Check if scheduled monitoring is enabled."""
    value = get_setting(db, "monitoring_enabled", "false")
    return value.lower() == "true"


def set_monitoring_enabled(db: Session, enabled: bool) -> None:
    """Enable or disable scheduled monitoring."""
    set_setting(db, "monitoring_enabled", "true" if enabled else "false")


def get_check_interval(db: Session) -> int:
    """Get the email check interval in minutes."""
    value = get_setting(db, "check_interval_minutes", "5")
    try:
        return int(value)
    except ValueError:
        return 5


def set_check_interval(db: Session, minutes: int) -> None:
    """Set the email check interval in minutes."""
    set_setting(db, "check_interval_minutes", str(minutes))


# =============================================================================
# Mobile Device Operations
# =============================================================================

from src.db.models import MobileDevice


def get_or_create_device(db: Session, device_id: str, device_name: Optional[str] = None) -> MobileDevice:
    """Get existing device or create a new one."""
    device = db.query(MobileDevice).filter(MobileDevice.device_id == device_id).first()
    if device:
        return device
    
    device = MobileDevice(
        device_id=device_id,
        device_name=device_name,
        notification_count=0,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device_sync(db: Session, device_id: str, notification_count: int) -> Optional[MobileDevice]:
    """Update device sync timestamp and increment notification count."""
    device = db.query(MobileDevice).filter(MobileDevice.device_id == device_id).first()
    if device:
        device.last_sync_at = datetime.utcnow()
        device.notification_count += notification_count
        db.commit()
        db.refresh(device)
    return device


def get_all_devices(db: Session) -> List[MobileDevice]:
    """Get all registered mobile devices."""
    return db.query(MobileDevice).order_by(MobileDevice.last_sync_at.desc()).all()


def get_device_count(db: Session) -> int:
    """Get total count of registered devices."""
    return db.query(func.count(MobileDevice.id)).scalar() or 0


def get_total_mobile_notifications(db: Session) -> int:
    """Get total notifications received from all mobile devices."""
    return db.query(func.sum(MobileDevice.notification_count)).scalar() or 0


def get_last_sync_time(db: Session) -> Optional[datetime]:
    """Get the most recent sync time across all devices."""
    device = db.query(MobileDevice).order_by(MobileDevice.last_sync_at.desc()).first()
    return device.last_sync_at if device else None


# =============================================================================
# Notification Query Operations
# =============================================================================

def get_notifications_by_source(
    db: Session,
    source_prefix: str,
    skip: int = 0,
    limit: int = 20,
) -> List[AlertHistory]:
    """Get notifications filtered by source prefix (e.g., 'android:whatsapp')."""
    query = db.query(AlertHistory)
    
    if source_prefix and source_prefix != "all":
        query = query.filter(AlertHistory.source.like(f"{source_prefix}%"))
    
    return query.order_by(AlertHistory.created_at.desc()).offset(skip).limit(limit).all()


def get_notification_count_by_source(db: Session, source_prefix: str) -> int:
    """Get count of notifications for a specific source prefix."""
    query = db.query(func.count(AlertHistory.id))
    
    if source_prefix and source_prefix != "all":
        query = query.filter(AlertHistory.source.like(f"{source_prefix}%"))
    
    return query.scalar() or 0


def get_notification_counts_by_source(db: Session) -> dict:
    """Get notification counts grouped by source."""
    # Get all unique sources and their counts
    results = db.query(
        AlertHistory.source,
        func.count(AlertHistory.id)
    ).group_by(AlertHistory.source).all()
    
    counts = {"all": 0}
    for source, count in results:
        counts[source] = count
        counts["all"] += count
        
        # Also aggregate by app type (e.g., android:whatsapp -> whatsapp)
        if source and ":" in source:
            app_name = source.split(":")[-1]
            if app_name not in counts:
                counts[app_name] = 0
            counts[app_name] += count
    
    return counts


# =============================================================================
# Mobile Command Operations (Cross-Platform Control)
# =============================================================================

from src.db.models import MobileCommand


def queue_mobile_command(
    db: Session,
    command: str,
    device_id: Optional[str] = None,
    payload: Optional[str] = None,
) -> MobileCommand:
    """Queue a command for mobile device(s) to execute.
    
    Args:
        db: Database session
        command: Command name (start_monitoring, stop_monitoring)
        device_id: Specific device ID, or None for all devices
        payload: Optional JSON payload
    """
    cmd = MobileCommand(
        device_id=device_id,
        command=command,
        payload=payload,
        executed=False,
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return cmd


def get_pending_commands(db: Session, device_id: str) -> List[MobileCommand]:
    """Get pending commands for a specific device."""
    return db.query(MobileCommand).filter(
        MobileCommand.executed == False,
        or_(
            MobileCommand.device_id == device_id,
            MobileCommand.device_id == None,  # Commands for all devices
        )
    ).order_by(MobileCommand.created_at.asc()).all()


def mark_command_executed(db: Session, command_id: int) -> bool:
    """Mark a command as executed."""
    cmd = db.query(MobileCommand).filter(MobileCommand.id == command_id).first()
    if cmd:
        cmd.executed = True
        cmd.executed_at = datetime.utcnow()
        db.commit()
        return True
    return False


def set_device_monitoring(db: Session, device_id: str, enabled: bool) -> Optional[MobileDevice]:
    """Set monitoring enabled/disabled for a specific device."""
    device = db.query(MobileDevice).filter(MobileDevice.device_id == device_id).first()
    if device:
        device.monitoring_enabled = enabled
        db.commit()
        db.refresh(device)
    return device


def set_all_devices_monitoring(db: Session, enabled: bool) -> int:
    """Set monitoring enabled/disabled for all devices. Returns count updated."""
    count = db.query(MobileDevice).update({MobileDevice.monitoring_enabled: enabled})
    db.commit()
    return count


def get_device_monitoring_status(db: Session, device_id: str) -> Optional[bool]:
    """Get monitoring status for a specific device."""
    device = db.query(MobileDevice).filter(MobileDevice.device_id == device_id).first()
    return device.monitoring_enabled if device else None


def get_global_monitoring_status(db: Session) -> dict:
    """Get unified monitoring status across all platforms."""
    email_enabled = get_monitoring_enabled(db)
    email_interval = get_check_interval(db)
    
    # Get mobile device stats
    devices = get_all_devices(db)
    mobile_enabled_count = sum(1 for d in devices if getattr(d, 'monitoring_enabled', True))
    total_devices = len(devices)
    
    return {
        "email_monitoring": {
            "enabled": email_enabled,
            "interval_minutes": email_interval,
        },
        "mobile_monitoring": {
            "total_devices": total_devices,
            "enabled_devices": mobile_enabled_count,
            "all_enabled": total_devices > 0 and mobile_enabled_count == total_devices,
        },
        "unified_enabled": email_enabled or (total_devices > 0 and mobile_enabled_count > 0),
    }
