package com.backend.mapper;

import com.backend.entity.BodyProfile;
import org.apache.ibatis.annotations.*;

@Mapper
public interface BodyProfileMapper {
    
    @Select("SELECT * FROM body_profile WHERE user_id = #{userId}")
    BodyProfile findByUserId(Long userId);
    
    @Insert("INSERT INTO body_profile (user_id, age, gender, height, weight, bmi, body_fat_rate, " +
            "vital_capacity, sit_and_reach, single_leg_stand, reaction_time, grip_strength, " +
            "max_oxygen_uptake, sit_ups_per_minute, push_ups, vertical_jump, high_knees_2min, " +
            "sit_to_stand_30s, exercise_preferences, uses_equipment, exercise_risk_level, diseases, " +
            "create_time, update_time) " +
            "VALUES (#{userId}, #{age}, #{gender}, #{height}, #{weight}, #{bmi}, #{bodyFatRate}, " +
            "#{vitalCapacity}, #{sitAndReach}, #{singleLegStand}, #{reactionTime}, #{gripStrength}, " +
            "#{maxOxygenUptake}, #{sitUpsPerMinute}, #{pushUps}, #{verticalJump}, #{highKnees2min}, " +
            "#{sitToStand30s}, #{exercisePreferences}, #{usesEquipment}, #{exerciseRiskLevel}, #{diseases}, " +
            "#{createTime}, #{updateTime})")
    int insert(BodyProfile bodyProfile);
    
    @Update("UPDATE body_profile SET age = #{age}, gender = #{gender}, height = #{height}, weight = #{weight}, " +
            "bmi = #{bmi}, body_fat_rate = #{bodyFatRate}, vital_capacity = #{vitalCapacity}, " +
            "sit_and_reach = #{sitAndReach}, single_leg_stand = #{singleLegStand}, reaction_time = #{reactionTime}, " +
            "grip_strength = #{gripStrength}, max_oxygen_uptake = #{maxOxygenUptake}, " +
            "sit_ups_per_minute = #{sitUpsPerMinute}, push_ups = #{pushUps}, vertical_jump = #{verticalJump}, " +
            "high_knees_2min = #{highKnees2min}, sit_to_stand_30s = #{sitToStand30s}, " +
            "exercise_preferences = #{exercisePreferences}, uses_equipment = #{usesEquipment}, " +
            "exercise_risk_level = #{exerciseRiskLevel}, diseases = #{diseases}, " +
            "update_time = #{updateTime} " +
            "WHERE user_id = #{userId}")
    int update(BodyProfile bodyProfile);
}
