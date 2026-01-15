package com.projectx.notificationmonitor.api

import com.projectx.notificationmonitor.data.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * API client for communicating with ProjectX backend.
 */
class ProjectXApiClient(private val config: ServerConfig) {
    
    private val api: ProjectXApi
    
    init {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
        
        val retrofit = Retrofit.Builder()
            .baseUrl(config.url.trimEnd('/') + "/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        api = retrofit.create(ProjectXApi::class.java)
    }
    
    /**
     * Test connection to the server.
     * Returns Result.success(true) if server is reachable.
     */
    suspend fun testConnection(): Result<Boolean> {
        return try {
            val response = api.healthCheck()
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Server returned ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Send a batch of notifications to the server.
     * Returns Result with the response on success.
     */
    suspend fun sendNotifications(
        deviceId: String,
        notifications: List<CapturedNotification>
    ): Result<NotificationBatchResponse> {
        if (notifications.isEmpty()) {
            return Result.success(NotificationBatchResponse(
                success = true,
                processed = 0,
                urgentCount = 0,
                message = "No notifications to send"
            ))
        }
        
        val request = NotificationBatchRequest(
            deviceId = deviceId,
            notifications = notifications.map { it.toPayload() }
        )
        
        return try {
            val authHeader = "Bearer ${config.apiKey}"
            val response = api.sendNotifications(authHeader, request)
            
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response body"))
            } else {
                val errorMsg = when (response.code()) {
                    401 -> "Invalid API key"
                    403 -> "Access denied"
                    else -> "Server error: ${response.code()}"
                }
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
