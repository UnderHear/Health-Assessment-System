package com.backend.mapper;

import com.backend.entity.TrainingCheckIn;
import org.apache.ibatis.annotations.*;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface TrainingCheckInMapper {
    
    @Select("SELECT * FROM training_check_in WHERE plan_id = #{planId} ORDER BY check_in_date DESC")
    List<TrainingCheckIn> findByPlanId(Long planId);
    
    @Select("SELECT * FROM training_check_in WHERE plan_id = #{planId} AND check_in_date = #{date}")
    TrainingCheckIn findByPlanIdAndDate(Long planId, LocalDate date);
    
    @Select("SELECT * FROM training_check_in WHERE plan_id = #{planId} AND week_number = #{weekNumber} ORDER BY check_in_date")
    List<TrainingCheckIn> findByPlanIdAndWeek(Long planId, Integer weekNumber);
    
    @Select("SELECT COUNT(*) FROM training_check_in WHERE plan_id = #{planId} AND completed = TRUE")
    int countCompletedByPlanId(Long planId);
    
    @Insert("INSERT INTO training_check_in (plan_id, user_id, check_in_date, week_number, " +
            "day_of_week, exercise_type, duration, avg_heart_rate, rpe, fatigue_level, completed, notes) " +
            "VALUES (#{planId}, #{userId}, #{checkInDate}, #{weekNumber}, #{dayOfWeek}, " +
            "#{exerciseType}, #{duration}, #{avgHeartRate}, #{rpe}, #{fatigueLevel}, #{completed}, #{notes})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(TrainingCheckIn checkIn);
    
    @Update("UPDATE training_check_in SET exercise_type = #{exerciseType}, completed = #{completed}, duration = #{duration}, " +
            "avg_heart_rate = #{avgHeartRate}, rpe = #{rpe}, fatigue_level = #{fatigueLevel}, notes = #{notes} WHERE id = #{id}")
    int update(TrainingCheckIn checkIn);
    
    @Delete("DELETE FROM training_check_in WHERE id = #{id}")
    int deleteById(Long id);
}
