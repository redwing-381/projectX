# Design Document: Android Notification Monitor

## Overview

The Android Notification Monitor is a companion app for ProjectX that captures notifications from messaging apps and forwards them to the backend for urgency classification. It uses Android's `NotificationListenerService` to intercept notifications and `WorkManager` for periodic background sync.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Android App                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │   MainActivity  │    │ NotificationService               │
│  │   (Settings UI) │    │ (Captures notifs)│                │
│  └────────┬────────┘    └────────┬────────┘                 │
│           │                      │                          │
│           ▼                      ▼                          │
│  ┌─────────────────────────────────────────┐                │
│  │         NotificationRepository          │                │
│  │    (Queue management, persistence)      │                │
│  └────────────────────┬────────────────────┘                │
│                       │                                     │
│           ┌───────────┴───────────┐                         │
│           ▼                       ▼                         │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  SharedPrefs    │    │   SyncWorker    │                 │
│  │  (Settings)     │    │  (Background)   │                 │
│  └─────────────────┘    └────────┬────────┘                 │
│                                  │                          │
└──────────────────────────────────┼──────────────────────────┘
                                   │
                                   ▼ HTTP POST
                          ┌─────────────────┐
                          │ ProjectX Server │
                          │   (Railway)     │
                          └─────────────────┘
```

## Components and Interfaces

### 1. NotificationListenerService

```kotlin
class NotificationService : NotificationListenerService() {
    // Called when notification is posted
    override fun onNotificationPosted(sbn: StatusBarNotification)
    
    // Called when notification is removed
    override fun onNotificationRemoved(sbn: StatusBarNotification)
}
```

### 2. Data Models

```kotlin
data class CapturedNotification(
    val id: String,           // UUID
    val appPackage: String,   // e.g., "com.whatsapp"
    val appName: String,      // e.g., "WhatsApp"
    val sender: String,       // Contact name or group
    val text: String,         // Message content
    val timestamp: Long,      // Unix timestamp
    val synced: Boolean       // Whether sent to server
)

data class AppConfig(
    val packageName: String,
    val displayName: String,
    val enabled: Boolean
)

data class ServerConfig(
    val url: String,
    val apiKey: String
)
```

### 3. Repository

```kotlin
class NotificationRepository(context: Context) {
    fun addNotification(notification: CapturedNotification)
    fun getUnsynced(): List<CapturedNotification>
    fun markSynced(ids: List<String>)
    fun clearSynced()
    fun getQueueSize(): Int
}
```

### 4. API Client

```kotlin
class ProjectXApiClient(config: ServerConfig) {
    suspend fun sendNotifications(notifications: List<CapturedNotification>): Result<Unit>
    suspend fun testConnection(): Result<Boolean>
}
```

### 5. SyncWorker

```kotlin
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result
}
```

## Data Models

### Notification Payload (to server)

```json
{
  "device_id": "unique-device-id",
  "notifications": [
    {
      "id": "uuid",
      "app": "WhatsApp",
      "sender": "Mom",
      "text": "Call me when you're free",
      "timestamp": 1705012345678
    }
  ]
}
```

### Server Response

```json
{
  "success": true,
  "processed": 5,
  "urgent_count": 1
}
```

## Supported Apps

| App | Package Name |
|-----|--------------|
| WhatsApp | com.whatsapp |
| Instagram | com.instagram.android |
| Telegram | org.telegram.messenger |
| Slack | com.Slack |
| Discord | com.discord |
| SMS/Messages | com.google.android.apps.messaging |
| Facebook Messenger | com.facebook.orca |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

### Property 1: Notification Capture Completeness

*For any* notification from a monitored app, the captured data SHALL contain non-empty app name, sender (or "Unknown"), message text, and valid timestamp.

**Validates: Requirements 1.1**

### Property 2: App Filter Enforcement

*For any* notification, it SHALL only be stored in the queue if its source app is in the user's selected apps list.

**Validates: Requirements 1.4, 2.3**

### Property 3: Duplicate Detection

*For any* two notifications with identical app, sender, and text arriving within 60 seconds, only the first SHALL be stored.

**Validates: Requirements 1.5**

### Property 4: Configuration Persistence

*For any* server configuration saved by the user, retrieving the configuration SHALL return the same URL and API key.

**Validates: Requirements 3.2**

### Property 5: Sync Queue Management

*For any* successful sync operation, all previously queued notifications SHALL be removed from the queue. *For any* failed sync operation, all notifications SHALL remain in the queue.

**Validates: Requirements 4.2, 4.3, 4.4**

## Error Handling

| Error | Handling |
|-------|----------|
| No notification permission | Show prompt to enable in settings |
| No internet | Skip sync, retry on next interval |
| Server unreachable | Retain queue, show error status |
| Invalid API key | Show authentication error |
| Server error (5xx) | Retain queue, retry later |

## Testing Strategy

### Unit Tests
- NotificationRepository: queue operations, persistence
- Duplicate detection logic
- App filter logic
- API client request formatting

### Property Tests
- Notification capture completeness
- App filter enforcement
- Duplicate detection within time window
- Configuration round-trip persistence
- Sync queue state management

### Integration Tests
- End-to-end notification capture to queue
- Sync worker execution
- Server communication

### Manual Tests
- Background operation
- Boot persistence
- Battery optimization handling
