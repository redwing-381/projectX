package com.projectx.notificationmonitor.service

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import com.projectx.notificationmonitor.data.CapturedNotification
import com.projectx.notificationmonitor.data.NotificationRepository
import com.projectx.notificationmonitor.data.SettingsManager
import com.projectx.notificationmonitor.data.SupportedApps

/**
 * Service that listens for notifications from messaging apps.
 * Requires user to grant notification access in Android settings.
 */
class NotificationService : NotificationListenerService() {
    
    private lateinit var repository: NotificationRepository
    private lateinit var settings: SettingsManager
    
    companion object {
        private const val TAG = "NotificationService"
    }
    
    override fun onCreate() {
        super.onCreate()
        repository = NotificationRepository(applicationContext)
        settings = SettingsManager(applicationContext)
        Log.d(TAG, "NotificationService created")
    }
    
    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        if (sbn == null) return
        
        val packageName = sbn.packageName
        
        // Check if this app is in our monitored list
        if (!settings.isAppEnabled(packageName)) {
            return
        }
        
        // Extract notification details
        val notification = sbn.notification ?: return
        val extras = notification.extras ?: return
        
        // Get sender (title) and text
        val sender = extractSender(extras, packageName)
        val text = extractText(extras)
        
        // Skip if no meaningful content
        if (text.isBlank()) {
            return
        }
        
        // Create captured notification
        val captured = CapturedNotification(
            appPackage = packageName,
            appName = SupportedApps.getDisplayName(packageName),
            sender = sender,
            text = text,
            timestamp = sbn.postTime
        )
        
        // Add to queue (repository handles duplicate detection)
        val added = repository.addNotification(captured)
        
        if (added) {
            Log.d(TAG, "Captured: ${captured.appName} - $sender: ${text.take(50)}...")
        } else {
            Log.d(TAG, "Duplicate notification ignored")
        }
    }
    
    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        // We don't need to handle removed notifications
    }
    
    /**
     * Extract sender name from notification extras.
     */
    private fun extractSender(extras: android.os.Bundle, packageName: String): String {
        // Try different keys used by various apps
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString()
        val conversationTitle = extras.getCharSequence(Notification.EXTRA_CONVERSATION_TITLE)?.toString()
        
        // For group chats, conversation title is the group name
        // For direct messages, title is the sender name
        return when {
            !conversationTitle.isNullOrBlank() -> conversationTitle
            !title.isNullOrBlank() -> title
            else -> "Unknown"
        }
    }
    
    /**
     * Extract message text from notification extras.
     */
    private fun extractText(extras: android.os.Bundle): String {
        // Try to get the main text
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString()
        val bigText = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString()
        
        // Prefer big text as it's usually more complete
        return when {
            !bigText.isNullOrBlank() -> bigText
            !text.isNullOrBlank() -> text
            else -> ""
        }
    }
}
