package com.backend.service;

import com.backend.entity.TrainingCheckIn;
import com.backend.entity.TrainingPlan;
import com.backend.entity.TestRecord;
import com.backend.mapper.TrainingCheckInMapper;
import com.backend.mapper.TrainingPlanMapper;
import com.backend.mapper.TestRecordMapper;
import com.backend.util.PlanDataParser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;

@Service
public class TrainingPlanService {
    
    @Autowired
    private TrainingPlanMapper planMapper;
    
    @Autowired
    private TrainingCheckInMapper checkInMapper;

    @Autowired
    private TestRecordMapper testRecordMapper;
    
    public List<TrainingPlan> getUserPlans(Long userId) {
        return planMapper.findByUserId(userId);
    }
    
    public TrainingPlan getPlanById(Long id) {
        return planMapper.findById(id);
    }
    
    public TrainingPlan getActivePlan(Long userId) {
        return planMapper.findActiveByUserId(userId);
    }
    
    @Transactional
    public TrainingPlan createPlan(TrainingPlan plan) {
        // 若绑定了体测报告，尝试提取分阶段训练周计划存入 plan_data
        if (plan.getTestRecordId() != null) {
            TestRecord record = testRecordMapper.findById(plan.getTestRecordId());
            if (record != null && StringUtils.hasText(record.getReport())) {
                String planData = PlanDataParser.buildPlanData(record.getReport(), plan.getTotalWeeks());
                plan.setPlanData(planData);
            }
        }
        planMapper.insert(plan);
        return plan;
    }
    
    @Transactional
    public void updatePlan(TrainingPlan plan) {
        planMapper.update(plan);
    }
    
    @Transactional
    public void deletePlan(Long id) {
        planMapper.deleteById(id);
    }
    
    public List<TrainingCheckIn> getPlanCheckIns(Long planId) {
        return checkInMapper.findByPlanId(planId);
    }
    
    public List<TrainingCheckIn> getWeekCheckIns(Long planId, Integer weekNumber) {
        return checkInMapper.findByPlanIdAndWeek(planId, weekNumber);
    }
    
    @Transactional
    public TrainingCheckIn checkIn(TrainingCheckIn checkIn) {
        TrainingCheckIn existing = checkInMapper.findByPlanIdAndDate(
            checkIn.getPlanId(), checkIn.getCheckInDate());
        
        if (existing != null) {
            checkIn.setId(existing.getId());
            checkInMapper.update(checkIn);
            return checkIn;
        } else {
            checkInMapper.insert(checkIn);
            return checkIn;
        }
    }
    
    public int getCompletedCount(Long planId) {
        return checkInMapper.countCompletedByPlanId(planId);
    }
    
    public int getCurrentWeek(TrainingPlan plan) {
        LocalDate now = LocalDate.now();
        if (now.isBefore(plan.getStartDate())) {
            return 1;
        }
        if (now.isAfter(plan.getEndDate())) {
            return plan.getTotalWeeks();
        }
        long daysBetween = ChronoUnit.DAYS.between(plan.getStartDate(), now);
        return (int) (daysBetween / 7) + 1;
    }

    public List<Map<String, Object>> getWeeklySchedule(TrainingPlan plan, int currentWeek) {
        if (plan == null || !StringUtils.hasText(plan.getPlanData())) {
            return List.of();
        }
        return PlanDataParser.buildWeeklySchedule(plan.getPlanData(), currentWeek);
    }
}
