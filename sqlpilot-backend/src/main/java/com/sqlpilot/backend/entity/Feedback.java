package com.sqlpilot.backend.entity;

import java.time.LocalDateTime;

public class Feedback {
    private String id;
    private String conversationId;
    private String userId;
    private Integer rating;
    private String comment;
    private String correctedAnswer;
    private Double reward;
    private LocalDateTime timestamp;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getConversationId() {
        return conversationId;
    }

    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public Integer getRating() {
        return rating;
    }

    public void setRating(Integer rating) {
        this.rating = rating;
    }

    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public String getCorrectedAnswer() {
        return correctedAnswer;
    }

    public void setCorrectedAnswer(String correctedAnswer) {
        this.correctedAnswer = correctedAnswer;
    }

    public Double getReward() {
        return reward;
    }

    public void setReward(Double reward) {
        this.reward = reward;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}