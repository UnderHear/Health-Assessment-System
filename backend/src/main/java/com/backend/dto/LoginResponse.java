package com.backend.dto;

import lombok.Data;

@Data
public class LoginResponse {
    private String token;
    private UserVO user;
    
    @Data
    public static class UserVO {
        private Long id;
        private String username;
        private String realName;
        private String email;
    }
}
