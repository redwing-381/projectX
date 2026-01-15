package com.projectx.notificationmonitor.api

import com.projectx.notificationmonitor.data.HealthResponse
import com.projectx.notificationmonitor.data.NotificationBatchRequest
import com.projectx.notificationmonitor.data.NotificationBatchResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST

/**
 * Retrofit interface for ProjectX API.
 */
interface ProjectXApi {
    
    @GET("health")
    suspend fun healthCheck(): Response<HealthResponse>
    
    @POST("api/notifications")
    suspend fun sendNotifications(
        @Header("Authorization") authorization: String,
        @Body request: NotificationBatchRequest
    ): Response<NotificationBatchResponse>
}
