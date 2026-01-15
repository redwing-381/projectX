package com.projectx.notificationmonitor.worker

import android.content.Context
import android.util.Log
import androidx.work.*
import com.projectx.notificationmonitor.api.ProjectXApiClient
import com.projectx.notificationmonitor.data.NotificationRepository
import com.projectx.notificationmonitor.data.SettingsManager
import java.util.concurrent.TimeUnit

/**
 * Background worker that syncs notifications to the server.
 */
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    private val repository = NotificationRepository(context)
    private val settings = SettingsManager(context)
    
    companion object {
        private const val TAG = "SyncWorker"
        private const val WORK_NAME = "notification_sync"
        
        /**
         * Schedule periodic sync with the configured interval.
         */
        fun schedule(context: Context) {
            val settings = SettingsManager(context)
            val interval = settings.getSyncInterval().toLong()
            
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            
            val request = PeriodicWorkRequestBuilder<SyncWorker>(
                interval, TimeUnit.MINUTES
            )
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    1, TimeUnit.MINUTES
                )
                .build()
            
            WorkManager.getInstance(context)
                .enqueueUniquePeriodicWork(
                    WORK_NAME,
                    ExistingPeriodicWorkPolicy.UPDATE,
                    request
                )
            
            Log.d(TAG, "Scheduled sync every $interval minutes")
        }
        
        /**
         * Cancel scheduled sync.
         */
        fun cancel(context: Context) {
            WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
            Log.d(TAG, "Cancelled scheduled sync")
        }
        
        /**
         * Trigger immediate sync.
         */
        fun syncNow(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            
            val request = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .build()
            
            WorkManager.getInstance(context).enqueue(request)
            Log.d(TAG, "Triggered immediate sync")
        }
    }
    
    override suspend fun doWork(): Result {
        Log.d(TAG, "Starting sync...")
        
        // Check if configured
        if (!settings.isConfigured()) {
            Log.w(TAG, "Not configured, skipping sync")
            settings.updateSyncStatus(false, "Not configured")
            return Result.success()
        }
        
        // Get unsynced notifications
        val unsynced = repository.getUnsynced()
        if (unsynced.isEmpty()) {
            Log.d(TAG, "No notifications to sync")
            settings.updateSyncStatus(true, "No new notifications")
            return Result.success()
        }
        
        Log.d(TAG, "Syncing ${unsynced.size} notifications...")
        
        // Send to server
        val client = ProjectXApiClient(settings.getServerConfig())
        val result = client.sendNotifications(
            deviceId = settings.getDeviceId(),
            notifications = unsynced
        )
        
        return result.fold(
            onSuccess = { response ->
                // Mark as synced
                val ids = unsynced.map { it.id }
                repository.markSynced(ids)
                repository.clearSynced()
                
                val message = "Synced ${response.processed}, ${response.urgentCount} urgent"
                Log.d(TAG, message)
                settings.updateSyncStatus(true, message)
                
                Result.success()
            },
            onFailure = { error ->
                val message = error.message ?: "Unknown error"
                Log.e(TAG, "Sync failed: $message")
                settings.updateSyncStatus(false, message)
                
                // Retry on network errors
                Result.retry()
            }
        )
    }
}
