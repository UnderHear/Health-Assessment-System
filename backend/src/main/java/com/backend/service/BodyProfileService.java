package com.backend.service;

import com.backend.entity.BodyProfile;
import com.backend.mapper.BodyProfileMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class BodyProfileService {
    
    @Autowired
    private BodyProfileMapper bodyProfileMapper;
    
    public BodyProfile getProfile(Long userId) {
        return bodyProfileMapper.findByUserId(userId);
    }
    
    public void saveOrUpdateProfile(BodyProfile profile) {
        BodyProfile existing = bodyProfileMapper.findByUserId(profile.getUserId());
        profile.setUpdateTime(LocalDateTime.now());
        
        if (existing == null) {
            profile.setCreateTime(LocalDateTime.now());
            bodyProfileMapper.insert(profile);
        } else {
            bodyProfileMapper.update(profile);
        }
    }
}
