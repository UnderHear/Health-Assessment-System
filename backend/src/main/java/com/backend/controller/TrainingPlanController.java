package com.backend.controller;

import com.backend.common.Result;
import com.backend.dto.CheckInRequest;
import com.backend.dto.TrainingPlanRequest;
import com.backend.entity.TrainingCheckIn;
import com.backend.entity.TrainingPlan;
import com.backend.service.TrainingPlanService;
import com.backend.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/training")
public class TrainingPlanController {
    
    @Autowired
    private TrainingPlanService trainingPlanService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    // 获取用户的所有计划
    @GetMapping("/plans")
    public Result<?> getUserPlans(@RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token);
        List<TrainingPlan> plans = trainingPlanService.getUserPlans(userId);
        return Result.success(plans);
    }
    
    // 获取当前活跃计划
    @GetMapping("/active-plan")
    public Result<?> getActivePlan(@RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token);
        TrainingPlan plan = trainingPlanService.getActivePlan(userId);
        
        if (plan == null) {
            return Result.success(null);
        }
        
        // 计算进度信息
        Map<String, Object> result = new HashMap<>();
        result.put("plan", plan);
        
        int currentWeek = trainingPlanService.getCurrentWeek(plan);
        plan.setCurrentWeek(currentWeek);
        trainingPlanService.updatePlan(plan);
        
        int completedCount = trainingPlanService.getCompletedCount(plan.getId());
        List<TrainingCheckIn> weekCheckIns = trainingPlanService.getWeekCheckIns(plan.getId(), currentWeek);
        
        result.put("currentWeek", currentWeek);
        result.put("totalCompleted", completedCount);
        result.put("weekCheckIns", weekCheckIns);
        
        // 计算总天数和剩余天数
        long totalDays = ChronoUnit.DAYS.between(plan.getStartDate(), plan.getEndDate()) + 1;
        long remainingDays = ChronoUnit.DAYS.between(LocalDate.now(), plan.getEndDate());
        remainingDays = Math.max(0, remainingDays);
        
        result.put("totalDays", totalDays);
        result.put("remainingDays", remainingDays);
        result.put("progress", totalDays > 0 ? (double)(totalDays - remainingDays) / totalDays * 100 : 0);
        
        return Result.success(result);
    }
    
    // 创建新计划
    @PostMapping("/create")
    public Result<?> createPlan(@RequestHeader("Authorization") String token,
                                @RequestBody TrainingPlanRequest request) {
        Long userId = jwtUtil.getUserIdFromToken(token);
        
        TrainingPlan plan = new TrainingPlan();
        plan.setUserId(userId);
        plan.setTestRecordId(request.getTestRecordId());
        plan.setPlanName(request.getPlanName());
        plan.setStartDate(request.getStartDate());
        plan.setTotalWeeks(request.getTotalWeeks());
        plan.setEndDate(request.getStartDate().plusWeeks(request.getTotalWeeks()));
        plan.setCurrentWeek(1);
        plan.setStatus("ACTIVE");
        
        trainingPlanService.createPlan(plan);
        return Result.success(plan);
    }
    
    // 打卡
    @PostMapping("/check-in")
    public Result<?> checkIn(@RequestHeader("Authorization") String token,
                            @RequestBody CheckInRequest request) {
        Long userId = jwtUtil.getUserIdFromToken(token);
        
        TrainingCheckIn checkIn = new TrainingCheckIn();
        checkIn.setPlanId(request.getPlanId());
        checkIn.setUserId(userId);
        checkIn.setCheckInDate(request.getCheckInDate());
        
        // 计算周数和星期
        TrainingPlan plan = trainingPlanService.getPlanById(request.getPlanId());
        long daysBetween = ChronoUnit.DAYS.between(plan.getStartDate(), request.getCheckInDate());
        int weekNumber = (int) (daysBetween / 7) + 1;
        int dayOfWeek = request.getCheckInDate().getDayOfWeek().getValue();
        
        checkIn.setWeekNumber(weekNumber);
        checkIn.setDayOfWeek(dayOfWeek);
        checkIn.setExerciseType(request.getExerciseType());
        checkIn.setDuration(request.getDuration());
        checkIn.setCompleted(request.getCompleted());
        checkIn.setNotes(request.getNotes());
        
        trainingPlanService.checkIn(checkIn);
        return Result.success(checkIn);
    }
    
    // 获取计划的打卡记录
    @GetMapping("/check-ins/{planId}")
    public Result<?> getCheckIns(@PathVariable Long planId) {
        List<TrainingCheckIn> checkIns = trainingPlanService.getPlanCheckIns(planId);
        return Result.success(checkIns);
    }
    
    // 获取某周的打卡记录
    @GetMapping("/check-ins/{planId}/week/{weekNumber}")
    public Result<?> getWeekCheckIns(@PathVariable Long planId, @PathVariable Integer weekNumber) {
        List<TrainingCheckIn> checkIns = trainingPlanService.getWeekCheckIns(planId, weekNumber);
        return Result.success(checkIns);
    }
    
    // 暂停计划
    @PutMapping("/pause/{planId}")
    public Result<?> pausePlan(@PathVariable Long planId) {
        TrainingPlan plan = trainingPlanService.getPlanById(planId);
        plan.setStatus("PAUSED");
        trainingPlanService.updatePlan(plan);
        return Result.success("计划已暂停");
    }
    
    // 恢复计划
    @PutMapping("/resume/{planId}")
    public Result<?> resumePlan(@PathVariable Long planId) {
        TrainingPlan plan = trainingPlanService.getPlanById(planId);
        plan.setStatus("ACTIVE");
        trainingPlanService.updatePlan(plan);
        return Result.success("计划已恢复");
    }
    
    // 完成计划
    @PutMapping("/complete/{planId}")
    public Result<?> completePlan(@PathVariable Long planId) {
        TrainingPlan plan = trainingPlanService.getPlanById(planId);
        plan.setStatus("COMPLETED");
        trainingPlanService.updatePlan(plan);
        return Result.success("恭喜完成计划！");
    }
    
    // 删除计划
    @DeleteMapping("/{planId}")
    public Result<?> deletePlan(@PathVariable Long planId) {
        trainingPlanService.deletePlan(planId);
        return Result.success("计划已删除");
    }
}
