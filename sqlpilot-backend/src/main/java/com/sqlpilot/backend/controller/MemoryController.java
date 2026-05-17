package com.sqlpilot.backend.controller;

import com.sqlpilot.backend.dto.request.FeedbackRequest;
import com.sqlpilot.backend.entity.SqlAnalysisHistory;
import com.sqlpilot.backend.service.MemoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/memory")
@CrossOrigin(origins = "*")
public class MemoryController {

    @Autowired
    private MemoryService memoryService;

    @PostMapping("/conversation")
    public ResponseEntity<Map<String, Object>> addConversation(
            @RequestParam String userId,
            @RequestParam String content,
            @RequestParam(defaultValue = "user") String role) {
        
        memoryService.addConversation(userId, content, role);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "对话记录已保存");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/conversation/{userId}")
    public ResponseEntity<Map<String, Object>> getConversationHistory(@PathVariable String userId) {
        List<SqlAnalysisHistory> history = memoryService.getConversationHistory(userId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", history);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/context/{userId}")
    public ResponseEntity<Map<String, Object>> getContextPrompt(@PathVariable String userId) {
        String context = memoryService.getContextPrompt(userId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("context", context);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/profile/{userId}")
    public ResponseEntity<Map<String, Object>> getUserProfile(@PathVariable String userId) {
        Map<String, Object> profile = memoryService.getUserProfile(userId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", profile);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/preference")
    public ResponseEntity<Map<String, Object>> updatePreference(
            @RequestParam String userId,
            @RequestParam String key,
            @RequestParam String value) {
        
        memoryService.updateUserPreference(userId, key, value);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "偏好设置已更新");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/feedback")
    public ResponseEntity<Map<String, Object>> submitFeedback(@RequestBody FeedbackRequest request) {
        String conversationId = request.getConversationId();
        String userId = request.getUserId();
        Integer rating = request.getRating();
        String comment = request.getComment();
        String correctedAnswer = request.getCorrectedAnswer();
        
        Map<String, Object> result = memoryService.recordFeedback(conversationId, userId, rating, comment, correctedAnswer);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("reward", result.get("reward"));
        response.put("needsUpdate", result.get("needsUpdate"));
        
        if (rating >= 4) {
            response.put("message", "感谢您的好评！");
            response.put("status", "positive");
        } else if (rating <= 2) {
            response.put("message", "抱歉未能满足您的需求，我们会持续改进");
            response.put("status", "negative");
        } else {
            response.put("message", "感谢您的反馈");
            response.put("status", "neutral");
        }
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/summary/{userId}")
    public ResponseEntity<Map<String, Object>> getConversationSummary(@PathVariable String userId) {
        String summary = memoryService.summarizeConversation(userId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("summary", summary);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/learning-report")
    public ResponseEntity<Map<String, Object>> getLearningReport(
            @RequestParam(required = false) String userId) {
        
        Map<String, Object> report = memoryService.getLearningReport(userId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", report);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/table-stats")
    public ResponseEntity<Map<String, Object>> getTableStats() {
        Map<String, Object> stats = memoryService.getTableStats();
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", stats);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/table-structure")
    public ResponseEntity<Map<String, Object>> getTableStructure() {
        Map<String, Object> structure = memoryService.getTableStructure();
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", structure);
        return ResponseEntity.ok(response);
    }
}
