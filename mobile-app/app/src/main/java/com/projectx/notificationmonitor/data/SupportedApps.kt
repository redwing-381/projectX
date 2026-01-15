package com.projectx.notificationmonitor.data

/**
 * List of supported messaging apps for notification monitoring.
 */
object SupportedApps {
    
    val apps = listOf(
        AppConfig(
            packageName = "com.whatsapp",
            displayName = "WhatsApp"
        ),
        AppConfig(
            packageName = "com.whatsapp.w4b",
            displayName = "WhatsApp Business"
        ),
        AppConfig(
            packageName = "com.instagram.android",
            displayName = "Instagram"
        ),
        AppConfig(
            packageName = "org.telegram.messenger",
            displayName = "Telegram"
        ),
        AppConfig(
            packageName = "com.Slack",
            displayName = "Slack"
        ),
        AppConfig(
            packageName = "com.discord",
            displayName = "Discord"
        ),
        AppConfig(
            packageName = "com.google.android.apps.messaging",
            displayName = "Messages (SMS)"
        ),
        AppConfig(
            packageName = "com.facebook.orca",
            displayName = "Messenger"
        ),
        AppConfig(
            packageName = "com.microsoft.teams",
            displayName = "Microsoft Teams"
        ),
        AppConfig(
            packageName = "com.linkedin.android",
            displayName = "LinkedIn"
        )
    )
    
    /**
     * Get display name for a package, or extract from package name if unknown.
     */
    fun getDisplayName(packageName: String): String {
        return apps.find { it.packageName == packageName }?.displayName
            ?: packageName.substringAfterLast(".").replaceFirstChar { it.uppercase() }
    }
    
    /**
     * Check if a package is a known messaging app.
     */
    fun isKnownApp(packageName: String): Boolean {
        return apps.any { it.packageName == packageName }
    }
}
