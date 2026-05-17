package com.sqlpilot.backend.entity;

import java.time.LocalDateTime;

public class UserProfile {
    private String userId;
    private String preferences;
    private String historySummary;
    private Double rating;
    private Integer totalInteractions;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getPreferences() {
        return preferences;
    }

    public void setPreferences(String preferences) {
        this.preferences = preferences;
    }

    public String getHistorySummary() {
        return historySummary;
    }

    public void setHistorySummary(String historySummary) {
        this.historySummary = historySummary;
    }

    public Double getRating() {
        return rating;
    }

    public void setRating(Double rating) {
        this.rating = rating;
    }

    public Integer getTotalInteractions() {
        return totalInteractions;
    }

    public void setTotalInteractions(Integer totalInteractions) {
        this.totalInteractions = totalInteractions;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}