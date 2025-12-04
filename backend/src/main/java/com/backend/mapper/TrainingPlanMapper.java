package com.backend.mapper;

import com.backend.entity.TrainingPlan;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface TrainingPlanMapper {
    
    @Select("SELECT * FROM training_plan WHERE user_id = #{userId} ORDER BY create_time DESC")
    List<TrainingPlan> findByUserId(Long userId);
    
    @Select("SELECT * FROM training_plan WHERE id = #{id}")
    TrainingPlan findById(Long id);
    
    @Select("SELECT * FROM training_plan WHERE user_id = #{userId} AND status = 'ACTIVE' ORDER BY create_time DESC LIMIT 1")
    TrainingPlan findActiveByUserId(Long userId);
    
    @Insert("INSERT INTO training_plan (user_id, test_record_id, plan_name, start_date, end_date, " +
            "total_weeks, current_week, status, plan_data) " +
            "VALUES (#{userId}, #{testRecordId}, #{planName}, #{startDate}, #{endDate}, " +
            "#{totalWeeks}, #{currentWeek}, #{status}, #{planData})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(TrainingPlan plan);
    
    @Update("UPDATE training_plan SET current_week = #{currentWeek}, status = #{status}, " +
            "update_time = NOW() WHERE id = #{id}")
    int update(TrainingPlan plan);
    
    @Delete("DELETE FROM training_plan WHERE id = #{id}")
    int deleteById(Long id);
}
