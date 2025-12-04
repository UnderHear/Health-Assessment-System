package com.backend.service;

import com.backend.entity.TestRecord;
import com.backend.mapper.TestRecordMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class TestRecordService {
    
    @Autowired
    private TestRecordMapper testRecordMapper;

    @Autowired
    private RestTemplate restTemplate;
    
    public TestRecord getLatestRecord(Long userId) {
        return testRecordMapper.findLatestByUserId(userId);
    }

    public List<TestRecord> getHistory(Long userId) {
        return testRecordMapper.findAllByUserId(userId);
    }

    public TestRecord getRecordById(Long id) {
        return testRecordMapper.findById(id);
    }

    public Map<String, Object> analyzeRecord(TestRecord record) {
        // 1. Insert new record with status GENERATING
        record.setId(null); // Ensure new record
        record.setCreateTime(LocalDateTime.now());
        record.setUpdateTime(LocalDateTime.now());
        record.setStatus("GENERATING");
        testRecordMapper.insert(record);

        try {
            // Convert TestRecord to Map with snake_case keys for Python backend
            Map<String, Object> requestData = new HashMap<>();
            requestData.put("age", record.getAge());
            requestData.put("gender", record.getGender());
            requestData.put("height", record.getHeight());
            requestData.put("weight", record.getWeight());
            requestData.put("bmi", record.getBmi());
            requestData.put("body_fat_rate", record.getBodyFatRate());
            requestData.put("vital_capacity", record.getVitalCapacity());
            requestData.put("sit_and_reach", record.getSitAndReach());
            requestData.put("single_leg_stand", record.getSingleLegStand());
            requestData.put("reaction_time", record.getReactionTime());
            requestData.put("grip_strength", record.getGripStrength());
            requestData.put("max_oxygen_uptake", record.getMaxOxygenUptake());
            requestData.put("sit_ups_per_minute", record.getSitUpsPerMinute());
            requestData.put("push_ups", record.getPushUps());
            requestData.put("vertical_jump", record.getVerticalJump());
            requestData.put("high_knees_2min", record.getHighKnees2min());
            requestData.put("sit_to_stand_30s", record.getSitToStand30s());
            requestData.put("name", "User"); // Default name

            // Handle lists (stored as comma-separated strings in DB/Entity)
            if (record.getExercisePreferences() != null && !record.getExercisePreferences().isEmpty()) {
                requestData.put("exercise_preferences", Arrays.asList(record.getExercisePreferences().split(",")));
            } else {
                requestData.put("exercise_preferences", new ArrayList<>());
            }

            requestData.put("uses_equipment", record.getUsesEquipment());
            requestData.put("exercise_risk_level", record.getExerciseRiskLevel());

            if (record.getDiseases() != null && !record.getDiseases().isEmpty()) {
                requestData.put("diseases", Arrays.asList(record.getDiseases().split(",")));
            } else {
                requestData.put("diseases", new ArrayList<>());
            }

            // Call Python service
            String pythonServiceUrl = "http://localhost:8000/analyze";
            Map<String, Object> responseMap = restTemplate.postForObject(pythonServiceUrl, requestData, Map.class);

            // 2. Update record with status COMPLETED and result
            if (responseMap != null && responseMap.containsKey("data")) {
                Map<String, Object> data = (Map<String, Object>) responseMap.get("data");
                
                record.setStatus("COMPLETED");
                record.setReport((String) data.get("report"));
                
                // Store individual scores/ratings as JSON
                ObjectMapper mapper = new ObjectMapper();
                Map<String, Object> analysisData = new HashMap<>();
                analysisData.put("individual_scores", data.get("individual_scores"));
                analysisData.put("individual_ratings", data.get("individual_ratings"));
                analysisData.put("overall_score", data.get("overall_score"));
                analysisData.put("overall_rating", data.get("overall_rating"));
                
                record.setAnalysisResult(mapper.writeValueAsString(analysisData));
                
                testRecordMapper.update(record);
                
                return data;
            } else {
                throw new RuntimeException("Invalid response from analysis service");
            }

        } catch (Exception e) {
            // 3. Update record with status FAILED
            record.setStatus("FAILED");
            record.setReport("Analysis failed: " + e.getMessage());
            testRecordMapper.update(record);
            throw new RuntimeException("Analysis failed", e);
        }
    }
}
