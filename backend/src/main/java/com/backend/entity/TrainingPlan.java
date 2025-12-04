package com.backend.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class TrainingPlan {
    private Long id;
    private Long userId;
    private Long testRecordId;
    private String planName;
    private LocalDate startDate;
    private LocalDate endDate;
    private Integer totalWeeks;
    private Integer currentWeek;
    private String status; // ACTIVE, COMPLETED, PAUSED
    private String planData; // JSON
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
