package com.backend.mapper;

import com.backend.entity.TestRecord;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface TestRecordMapper {
    
    @Select("SELECT * FROM test_record WHERE user_id = #{userId} ORDER BY create_time DESC LIMIT 1")
    TestRecord findLatestByUserId(Long userId);

    @Select("SELECT * FROM test_record WHERE user_id = #{userId} ORDER BY create_time DESC")
    List<TestRecord> findAllByUserId(Long userId);

    @Select("SELECT * FROM test_record WHERE id = #{id}")
    TestRecord findById(Long id);
    
    @Insert("INSERT INTO test_record (user_id, age, gender, height, weight, bmi, body_fat_rate, " +
            "vital_capacity, sit_and_reach, single_leg_stand, reaction_time, grip_strength, " +
            "max_oxygen_uptake, sit_ups_per_minute, push_ups, vertical_jump, high_knees_2min, " +
            "sit_to_stand_30s, exercise_preferences, uses_equipment, exercise_risk_level, diseases, " +
            "report, status, analysis_result, create_time, update_time) " +
            "VALUES (#{userId}, #{age}, #{gender}, #{height}, #{weight}, #{bmi}, #{bodyFatRate}, " +
            "#{vitalCapacity}, #{sitAndReach}, #{singleLegStand}, #{reactionTime}, #{gripStrength}, " +
            "#{maxOxygenUptake}, #{sitUpsPerMinute}, #{pushUps}, #{verticalJump}, #{highKnees2min}, " +
            "#{sitToStand30s}, #{exercisePreferences}, #{usesEquipment}, #{exerciseRiskLevel}, #{diseases}, " +
            "#{report}, #{status}, #{analysisResult}, #{createTime}, #{updateTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(TestRecord testRecord);
    
    @Update("UPDATE test_record SET age = #{age}, gender = #{gender}, height = #{height}, weight = #{weight}, " +
            "bmi = #{bmi}, body_fat_rate = #{bodyFatRate}, vital_capacity = #{vitalCapacity}, " +
            "sit_and_reach = #{sitAndReach}, single_leg_stand = #{singleLegStand}, reaction_time = #{reactionTime}, " +
            "grip_strength = #{gripStrength}, max_oxygen_uptake = #{maxOxygenUptake}, " +
            "sit_ups_per_minute = #{sitUpsPerMinute}, push_ups = #{pushUps}, vertical_jump = #{verticalJump}, " +
            "high_knees_2min = #{highKnees2min}, sit_to_stand_30s = #{sitToStand30s}, " +
            "exercise_preferences = #{exercisePreferences}, uses_equipment = #{usesEquipment}, " +
            "exercise_risk_level = #{exerciseRiskLevel}, diseases = #{diseases}, " +
            "report = #{report}, status = #{status}, analysis_result = #{analysisResult}, " +
            "update_time = #{updateTime} " +
            "WHERE id = #{id}")
    int update(TestRecord testRecord);
}
