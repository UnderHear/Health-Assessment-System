package com.backend.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class BodyProfile {
    private Long userId;
    private Integer age;
    private String gender;
    private Double height;
    private Double weight;
    private Double bmi;
    private Double bodyFatRate;
    private Integer vitalCapacity;
    private Double sitAndReach;
    private Double singleLegStand;
    private Double reactionTime;
    private Double gripStrength;
    private Double maxOxygenUptake;
    private Integer sitUpsPerMinute;
    private Integer pushUps;
    private Double verticalJump;
    private Integer highKnees2min;
    private Integer sitToStand30s;
    private String exercisePreferences;
    private Boolean usesEquipment;
    private String exerciseRiskLevel;
    private String diseases;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
