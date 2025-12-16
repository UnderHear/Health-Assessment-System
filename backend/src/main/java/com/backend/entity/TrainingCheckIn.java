package com.backend.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class TrainingCheckIn {
    private Long id;
    private Long planId;
    private Long userId;
    private LocalDate checkInDate;
    private Integer weekNumber;
    private Integer dayOfWeek;
    private String exerciseType;
    private Integer duration;
    private Integer avgHeartRate;
    private Integer rpe;
    private String fatigueLevel;
    private Boolean completed;
    private String notes;
    private LocalDateTime createTime;
}
