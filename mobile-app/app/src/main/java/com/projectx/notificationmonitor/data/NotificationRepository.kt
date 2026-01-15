package com.projectx.notificationmonitor.data

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/**
 * Repository for managing captured notifications queue.
 * Uses SharedPreferences for persistence.
 */
class NotificationRepository(context: Context) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME, Context.MODE_PRIVATE
    )
    private val gson = Gson()
    
    companion object {
        private const val PREFS_NAME = "notification_queue"
        private const val KEY_NOTIFICATIONS = "notifications"
        private const val KEY_RECENT_HASHES = "recent_hashes"
        private const val DUPLICATE_WINDOW_MS = 60_000L // 1 minute
    }
    
    /**
     * Add a notification to the queue if it's not a duplicate.
     * Returns true if added, false if duplicate.
     */
    @Synchronized
    fun addNotification(notification: CapturedNotification): Boolean {
        // Check for duplicates
        val hash = generateHash(notification)
        if (isDuplicate(hash, notification.timestamp)) {
            return false
        }
        
        // Add to queue
        val notifications = getAll().toMutableList()
        notifications.add(notification)
        saveAll(notifications)
        
        // Track hash for duplicate detection
        trackHash(hash, notification.timestamp)
        
        return true
    }
    
    /**
     * Get all unsynced notifications.
     */
    fun getUnsynced(): List<CapturedNotification> {
        return getAll().filter { !it.synced }
    }
    
    /**
     * Mark notifications as synced by their IDs.
     */
    @Synchronized
    fun markSynced(ids: List<String>) {
        val notifications = getAll().toMutableList()
        notifications.forEach { notification ->
            if (ids.contains(notification.id)) {
                notification.synced = true
            }
        }
        saveAll(notifications)
    }
    
    /**
     * Clear all synced notifications from the queue.
     */
    @Synchronized
    fun clearSynced() {
        val notifications = getAll().filter { !it.synced }
        saveAll(notifications)
    }
    
    /**
     * Get the number of notifications in queue.
     */
    fun getQueueSize(): Int {
        return getUnsynced().size
    }
    
    /**
     * Get all notifications (for debugging).
     */
    fun getAll(): List<CapturedNotification> {
        val json = prefs.getString(KEY_NOTIFICATIONS, null) ?: return emptyList()
        val type = object : TypeToken<List<CapturedNotification>>() {}.type
        return try {
            gson.fromJson(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    /**
     * Clear all notifications (for testing/reset).
     */
    @Synchronized
    fun clearAll() {
        prefs.edit()
            .remove(KEY_NOTIFICATIONS)
            .remove(KEY_RECENT_HASHES)
            .apply()
    }
    
    private fun saveAll(notifications: List<CapturedNotification>) {
        val json = gson.toJson(notifications)
        prefs.edit().putString(KEY_NOTIFICATIONS, json).apply()
    }
    
    /**
     * Generate a hash for duplicate detection.
     */
    private fun generateHash(notification: CapturedNotification): String {
        return "${notification.appPackage}|${notification.sender}|${notification.text}".hashCode().toString()
    }
    
    /**
     * Check if a notification hash is a duplicate within the time window.
     */
    private fun isDuplicate(hash: String, timestamp: Long): Boolean {
        val recentHashes = getRecentHashes()
        val existingTimestamp = recentHashes[hash] ?: return false
        return (timestamp - existingTimestamp) < DUPLICATE_WINDOW_MS
    }
    
    /**
     * Track a hash with its timestamp for duplicate detection.
     */
    private fun trackHash(hash: String, timestamp: Long) {
        val recentHashes = getRecentHashes().toMutableMap()
        
        // Clean up old hashes (older than 5 minutes)
        val cutoff = System.currentTimeMillis() - (5 * 60 * 1000)
        recentHashes.entries.removeIf { it.value < cutoff }
        
        // Add new hash
        recentHashes[hash] = timestamp
        
        // Save
        val json = gson.toJson(recentHashes)
        prefs.edit().putString(KEY_RECENT_HASHES, json).apply()
    }
    
    private fun getRecentHashes(): Map<String, Long> {
        val json = prefs.getString(KEY_RECENT_HASHES, null) ?: return emptyMap()
        val type = object : TypeToken<Map<String, Long>>() {}.type
        return try {
            gson.fromJson(json, type) ?: emptyMap()
        } catch (e: Exception) {
            emptyMap()
        }
    }
}
