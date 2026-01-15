package com.projectx.notificationmonitor.data

import com.google.gson.annotations.SerializedName
import java.util.UUID

/**
 * Represents a captured notification from a messaging app.
 */
data class CapturedNotification(
    val id: String = UUID.randomUUID().toString(),
    val appPackage: String,
    val appName: String,
    val sender: String,
    val text: String,
    val timestamp: Long = System.currentTimeMillis(),
    var synced: Boolean = false
)

/**
 * Configuration for a monitored app.
 */
data class AppConfig(
    val packageName: String,
    val displayName: String,
    var enabled: Boolean = false
)

/**
 * Server configuration for API communication.
 */
data class ServerConfig(
    val url: String,
    val apiKey: String
) {
    fun isValid(): Boolean = url.isNotBlank() && apiKey.isNotBlank()
}

/**
 * Request payload for sending notifications to server.
 */
data class NotificationBatchRequest(
    @SerializedName("device_id")
    val deviceId: String,
    val notifications: List<NotificationPayload>
)

/**
 * Individual notification in the batch request.
 */
data class NotificationPayload(
    val id: String,
    val app: String,
    val sender: String,
    val text: String,
    val timestamp: Long
)

/**
 * Response from the server after processing notifications.
 */
data class NotificationBatchResponse(
    val success: Boolean,
    val processed: Int,
    @SerializedName("urgent_count")
    val urgentCount: Int,
    val message: String? = null
)

/**
 * Health check response from server.
 */
data class HealthResponse(
    val status: String,
    @SerializedName("app_name")
    val appName: String?
)

/**
 * Extension function to convert CapturedNotification to API payload.
 */
fun CapturedNotification.toPayload(): NotificationPayload {
    return NotificationPayload(
        id = id,
        app = appName,
        sender = sender,
        text = text,
        timestamp = timestamp
    )
}
