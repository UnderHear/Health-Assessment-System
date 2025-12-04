package com.backend.controller;

import com.backend.common.Result;
import com.backend.entity.BodyProfile;
import com.backend.entity.TestRecord;
import com.backend.service.BodyProfileService;
import com.backend.service.TestRecordService;
import com.backend.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/profile")
@CrossOrigin(origins = "*")
public class UserProfileController {
    
    @Autowired
    private BodyProfileService bodyProfileService;

    @Autowired
    private TestRecordService testRecordService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @GetMapping
    public Result<BodyProfile> getProfile(@RequestHeader("Authorization") String token) {
        try {
            Long userId = jwtUtil.getUserIdFromToken(token);
            BodyProfile profile = bodyProfileService.getProfile(userId);
            return Result.success(profile);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/history")
    public Result<List<TestRecord>> getHistory(@RequestHeader("Authorization") String token) {
        try {
            Long userId = jwtUtil.getUserIdFromToken(token);
            List<TestRecord> history = testRecordService.getHistory(userId);
            return Result.success(history);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/{id:[0-9]+}")
    public Result<TestRecord> getProfileById(@PathVariable Long id) {
        try {
            TestRecord profile = testRecordService.getRecordById(id);
            return Result.success(profile);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @PostMapping
    public Result<Void> saveProfile(@RequestHeader("Authorization") String token, @RequestBody BodyProfile profile) {
        try {
            Long userId = jwtUtil.getUserIdFromToken(token);
            profile.setUserId(userId);
            bodyProfileService.saveOrUpdateProfile(profile);
            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/analyze")
    public Result<Map<String, Object>> analyzeProfile(@RequestHeader("Authorization") String token, @RequestBody TestRecord profile) {
        try {
            Long userId = jwtUtil.getUserIdFromToken(token);
            profile.setUserId(userId);
            
            // Service now handles insertion and update
            Map<String, Object> analysisResult = testRecordService.analyzeRecord(profile);
            
            return Result.success(analysisResult);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
}
