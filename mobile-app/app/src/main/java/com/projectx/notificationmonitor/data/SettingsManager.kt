package com.projectx.notificationmonitor.data

import android.content.Context
import android.content.SharedPreferences
import android.provider.Settings
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/**
 * Manages app settings and configuration persistence.
 */
class SettingsManager(private val context: Context) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME, Context.MODE_PRIVATE
    )
    private val gson = Gson()
    
    companion object {
        private const val PREFS_NAME = "projectx_settings"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_API_KEY = "api_key"
        private const val KEY_ENABLED_APPS = "enabled_apps"
        private const val KEY_SYNC_INTERVAL = "sync_interval"
        private const val KEY_MONITORING_ENABLED = "monitoring_enabled"
        private const val KEY_LAST_SYNC_TIME = "last_sync_time"
        private const val KEY_LAST_SYNC_SUCCESS = "last_sync_success"
        private const val KEY_LAST_SYNC_MESSAGE = "last_sync_message"
        
        const val DEFAULT_SYNC_INTERVAL = 10 // minutes
        const val DEFAULT_SERVER_URL = "https://projectx-production-0eeb.up.railway.app"
    }
    
    // Server Configuration
    
    fun getServerUrl(): String {
        return prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
    }
    
    fun setServerUrl(url: String) {
        prefs.edit().putString(KEY_SERVER_URL, url.trimEnd('/')).apply()
    }
    
    fun getApiKey(): String {
        return prefs.getString(KEY_API_KEY, "") ?: ""
    }
    
    fun setApiKey(apiKey: String) {
        prefs.edit().putString(KEY_API_KEY, apiKey).apply()
    }
    
    fun getServerConfig(): ServerConfig {
        return ServerConfig(
            url = getServerUrl(),
            apiKey = getApiKey()
        )
    }
    
    fun isConfigured(): Boolean {
        return getApiKey().isNotBlank()
    }
    
    // App Selection
    
    fun getEnabledApps(): Set<String> {
        val json = prefs.getString(KEY_ENABLED_APPS, null)
        if (json == null) {
            // Default: enable WhatsApp and SMS
            return setOf("com.whatsapp", "com.google.android.apps.messaging")
        }
        val type = object : TypeToken<Set<String>>() {}.type
        return try {
            gson.fromJson(json, type) ?: emptySet()
        } catch (e: Exception) {
            emptySet()
        }
    }
    
    fun setEnabledApps(packageNames: Set<String>) {
        val json = gson.toJson(packageNames)
        prefs.edit().putString(KEY_ENABLED_APPS, json).apply()
    }
    
    fun isAppEnabled(packageName: String): Boolean {
        return getEnabledApps().contains(packageName)
    }
    
    fun toggleApp(packageName: String, enabled: Boolean) {
        val apps = getEnabledApps().toMutableSet()
        if (enabled) {
            apps.add(packageName)
        } else {
            apps.remove(packageName)
        }
        setEnabledApps(apps)
    }
    
    // Sync Settings
    
    fun getSyncInterval(): Int {
        return prefs.getInt(KEY_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL)
    }
    
    fun setSyncInterval(minutes: Int) {
        prefs.edit().putInt(KEY_SYNC_INTERVAL, minutes.coerceIn(1, 60)).apply()
    }
    
    // Monitoring State
    
    fun isMonitoringEnabled(): Boolean {
        return prefs.getBoolean(KEY_MONITORING_ENABLED, false)
    }
    
    fun setMonitoringEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_MONITORING_ENABLED, enabled).apply()
    }
    
    // Sync Status
    
    fun getLastSyncTime(): Long {
        return prefs.getLong(KEY_LAST_SYNC_TIME, 0)
    }
    
    fun getLastSyncSuccess(): Boolean {
        return prefs.getBoolean(KEY_LAST_SYNC_SUCCESS, true)
    }
    
    fun getLastSyncMessage(): String {
        return prefs.getString(KEY_LAST_SYNC_MESSAGE, "") ?: ""
    }
    
    fun updateSyncStatus(success: Boolean, message: String = "") {
        prefs.edit()
            .putLong(KEY_LAST_SYNC_TIME, System.currentTimeMillis())
            .putBoolean(KEY_LAST_SYNC_SUCCESS, success)
            .putString(KEY_LAST_SYNC_MESSAGE, message)
            .apply()
    }
    
    // Device ID
    
    fun getDeviceId(): String {
        return Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
            ?: "unknown-device"
    }
}
