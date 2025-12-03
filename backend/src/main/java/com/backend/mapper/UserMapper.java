package com.backend.mapper;

import com.backend.entity.User;
import org.apache.ibatis.annotations.*;

@Mapper
public interface UserMapper {
    
    @Select("SELECT * FROM user WHERE username = #{username}")
    User findByUsername(String username);
    
    @Select("SELECT * FROM user WHERE id = #{id}")
    User findById(Long id);
    
    @Insert("INSERT INTO user (username, password, real_name, email, status, create_time, update_time) " +
            "VALUES (#{username}, #{password}, #{realName}, #{email}, #{status}, #{createTime}, #{updateTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
    
    @Update("UPDATE user SET password = #{password}, real_name = #{realName}, email = #{email}, " +
            "update_time = #{updateTime} WHERE id = #{id}")
    int update(User user);
}
