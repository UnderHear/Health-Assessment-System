package com.backend.service;

import com.backend.entity.TrainingCheckIn;
import com.backend.entity.TrainingPlan;
import com.backend.mapper.TrainingCheckInMapper;
import com.backend.mapper.TrainingPlanMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Service
public class TrainingPlanService {
    
    @Autowired
    private TrainingPlanMapper planMapper;
    
    @Autowired
    private TrainingCheckInMapper checkInMapper;
    
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
}
