package com.projectx.notificationmonitor

import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.projectx.notificationmonitor.api.ProjectXApiClient
import com.projectx.notificationmonitor.data.NotificationRepository
import com.projectx.notificationmonitor.data.SettingsManager
import com.projectx.notificationmonitor.data.SupportedApps
import com.projectx.notificationmonitor.databinding.ActivityMainBinding
import com.projectx.notificationmonitor.service.NotificationService
import com.projectx.notificationmonitor.worker.SyncWorker
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var settings: SettingsManager
    private lateinit var repository: NotificationRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        settings = SettingsManager(this)
        repository = NotificationRepository(this)
        
        setupUI()
        loadSettings()
        updateStatus()
    }
    
    override fun onResume() {
        super.onResume()
        updateStatus()
    }
    
    private fun setupUI() {
        // Server configuration
        binding.btnTestConnection.setOnClickListener { testConnection() }
        binding.btnSaveConfig.setOnClickListener { saveConfig() }
        
        // Notification access
        binding.btnEnableAccess.setOnClickListener { openNotificationSettings() }
        
        // Sync controls
        binding.btnSyncNow.setOnClickListener { syncNow() }
        binding.btnToggleMonitoring.setOnClickListener { toggleMonitoring() }
        
        // App selection checkboxes
        setupAppCheckboxes()
        
        // Sync interval spinner
        setupSyncIntervalSpinner()
    }
    
    private fun setupAppCheckboxes() {
        val enabledApps = settings.getEnabledApps()
        
        binding.checkWhatsapp.isChecked = enabledApps.contains("com.whatsapp")
        binding.checkInstagram.isChecked = enabledApps.contains("com.instagram.android")
        binding.checkTelegram.isChecked = enabledApps.contains("org.telegram.messenger")
        binding.checkSlack.isChecked = enabledApps.contains("com.Slack")
        binding.checkDiscord.isChecked = enabledApps.contains("com.discord")
        binding.checkSms.isChecked = enabledApps.contains("com.google.android.apps.messaging")
        binding.checkMessenger.isChecked = enabledApps.contains("com.facebook.orca")
        
        // Set listeners
        binding.checkWhatsapp.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.whatsapp", checked)
        }
        binding.checkInstagram.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.instagram.android", checked)
        }
        binding.checkTelegram.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("org.telegram.messenger", checked)
        }
        binding.checkSlack.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.Slack", checked)
        }
        binding.checkDiscord.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.discord", checked)
        }
        binding.checkSms.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.google.android.apps.messaging", checked)
        }
        binding.checkMessenger.setOnCheckedChangeListener { _, checked ->
            settings.toggleApp("com.facebook.orca", checked)
        }
    }
    
    private fun setupSyncIntervalSpinner() {
        val intervals = arrayOf("5 minutes", "10 minutes", "15 minutes", "30 minutes")
        val intervalValues = arrayOf(5, 10, 15, 30)
        
        val adapter = android.widget.ArrayAdapter(this, android.R.layout.simple_spinner_item, intervals)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerInterval.adapter = adapter
        
        // Set current value
        val currentInterval = settings.getSyncInterval()
        val index = intervalValues.indexOf(currentInterval).coerceAtLeast(0)
        binding.spinnerInterval.setSelection(index)
        
        binding.spinnerInterval.onItemSelectedListener = object : android.widget.AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: android.widget.AdapterView<*>?, view: View?, position: Int, id: Long) {
                settings.setSyncInterval(intervalValues[position])
                if (settings.isMonitoringEnabled()) {
                    SyncWorker.schedule(this@MainActivity)
                }
            }
            override fun onNothingSelected(parent: android.widget.AdapterView<*>?) {}
        }
    }
    
    private fun loadSettings() {
        binding.editServerUrl.setText(settings.getServerUrl())
        binding.editApiKey.setText(settings.getApiKey())
    }
    
    private fun saveConfig() {
        val url = binding.editServerUrl.text.toString().trim()
        val apiKey = binding.editApiKey.text.toString().trim()
        
        if (url.isBlank()) {
            Toast.makeText(this, "Server URL is required", Toast.LENGTH_SHORT).show()
            return
        }
        if (apiKey.isBlank()) {
            Toast.makeText(this, "API Key is required", Toast.LENGTH_SHORT).show()
            return
        }
        
        settings.setServerUrl(url)
        settings.setApiKey(apiKey)
        Toast.makeText(this, "Configuration saved", Toast.LENGTH_SHORT).show()
        updateStatus()
    }
    
    private fun testConnection() {
        val url = binding.editServerUrl.text.toString().trim()
        if (url.isBlank()) {
            Toast.makeText(this, "Enter server URL first", Toast.LENGTH_SHORT).show()
            return
        }
        
        binding.btnTestConnection.isEnabled = false
        binding.btnTestConnection.text = "Testing..."
        
        lifecycleScope.launch {
            val client = ProjectXApiClient(settings.getServerConfig().copy(url = url))
            val result = client.testConnection()
            
            binding.btnTestConnection.isEnabled = true
            binding.btnTestConnection.text = "Test Connection"
            
            result.fold(
                onSuccess = {
                    Toast.makeText(this@MainActivity, "✓ Connection successful!", Toast.LENGTH_SHORT).show()
                },
                onFailure = { error ->
                    Toast.makeText(this@MainActivity, "✗ Failed: ${error.message}", Toast.LENGTH_LONG).show()
                }
            )
        }
    }
    
    private fun updateStatus() {
        // Notification access status
        val hasAccess = isNotificationAccessEnabled()
        binding.textAccessStatus.text = if (hasAccess) "✓ Enabled" else "✗ Not enabled"
        binding.textAccessStatus.setTextColor(
            if (hasAccess) getColor(android.R.color.holo_green_dark)
            else getColor(android.R.color.holo_red_dark)
        )
        binding.btnEnableAccess.visibility = if (hasAccess) View.GONE else View.VISIBLE
        
        // Configuration status
        val isConfigured = settings.isConfigured()
        binding.textConfigStatus.text = if (isConfigured) "✓ Configured" else "✗ Not configured"
        binding.textConfigStatus.setTextColor(
            if (isConfigured) getColor(android.R.color.holo_green_dark)
            else getColor(android.R.color.holo_red_dark)
        )
        
        // Queue size
        val queueSize = repository.getQueueSize()
        binding.textQueueSize.text = "$queueSize notifications pending"
        
        // Last sync
        val lastSync = settings.getLastSyncTime()
        if (lastSync > 0) {
            val dateFormat = SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault())
            val success = settings.getLastSyncSuccess()
            val message = settings.getLastSyncMessage()
            val status = if (success) "✓" else "✗"
            binding.textLastSync.text = "$status ${dateFormat.format(Date(lastSync))}\n$message"
        } else {
            binding.textLastSync.text = "Never synced"
        }
        
        // Monitoring toggle
        val isMonitoring = settings.isMonitoringEnabled()
        binding.btnToggleMonitoring.text = if (isMonitoring) "Stop Monitoring" else "Start Monitoring"
    }
    
    private fun toggleMonitoring() {
        val isMonitoring = settings.isMonitoringEnabled()
        
        if (!isMonitoring) {
            // Starting monitoring
            if (!isNotificationAccessEnabled()) {
                Toast.makeText(this, "Enable notification access first", Toast.LENGTH_SHORT).show()
                openNotificationSettings()
                return
            }
            if (!settings.isConfigured()) {
                Toast.makeText(this, "Configure server settings first", Toast.LENGTH_SHORT).show()
                return
            }
            
            settings.setMonitoringEnabled(true)
            SyncWorker.schedule(this)
            Toast.makeText(this, "Monitoring started", Toast.LENGTH_SHORT).show()
        } else {
            // Stopping monitoring
            settings.setMonitoringEnabled(false)
            SyncWorker.cancel(this)
            Toast.makeText(this, "Monitoring stopped", Toast.LENGTH_SHORT).show()
        }
        
        updateStatus()
    }
    
    private fun syncNow() {
        if (!settings.isConfigured()) {
            Toast.makeText(this, "Configure server settings first", Toast.LENGTH_SHORT).show()
            return
        }
        
        SyncWorker.syncNow(this)
        Toast.makeText(this, "Sync triggered", Toast.LENGTH_SHORT).show()
    }
    
    private fun openNotificationSettings() {
        val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
        startActivity(intent)
    }
    
    private fun isNotificationAccessEnabled(): Boolean {
        val cn = ComponentName(this, NotificationService::class.java)
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
        return flat != null && flat.contains(cn.flattenToString())
    }
}
