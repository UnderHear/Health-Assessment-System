package com.backend.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class CheckInRequest {
    private Long planId;
    private LocalDate checkInDate;
    private String exerciseType;
    private Integer duration;
    private Boolean completed;
    private String notes;
}
