package com.projectx.notificationmonitor.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.projectx.notificationmonitor.data.SettingsManager
import com.projectx.notificationmonitor.worker.SyncWorker

/**
 * Receiver that restarts monitoring after device boot.
 */
class BootReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "BootReceiver"
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) {
            return
        }
        
        Log.d(TAG, "Boot completed, checking monitoring state...")
        
        val settings = SettingsManager(context)
        
        if (settings.isMonitoringEnabled() && settings.isConfigured()) {
            Log.d(TAG, "Restarting sync worker...")
            SyncWorker.schedule(context)
        } else {
            Log.d(TAG, "Monitoring not enabled or not configured")
        }
    }
}
