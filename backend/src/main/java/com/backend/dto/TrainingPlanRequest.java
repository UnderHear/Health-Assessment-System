package com.backend.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class TrainingPlanRequest {
    private Long testRecordId;
    private String planName;
    private LocalDate startDate;
    private Integer totalWeeks;
}
