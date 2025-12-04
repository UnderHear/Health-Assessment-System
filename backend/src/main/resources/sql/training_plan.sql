-- 训练计划表
CREATE TABLE IF NOT EXISTS training_plan (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    test_record_id BIGINT NOT NULL COMMENT '关联的测试记录ID',
    plan_name VARCHAR(100) NOT NULL COMMENT '计划名称',
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE NOT NULL COMMENT '结束日期',
    total_weeks INT NOT NULL COMMENT '总周数',
    current_week INT DEFAULT 1 COMMENT '当前周数',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE-进行中, COMPLETED-已完成, PAUSED-已暂停',
    plan_data TEXT COMMENT '计划详细数据(JSON)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_test_record_id (test_record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='训练计划表';

-- 训练打卡记录表
CREATE TABLE IF NOT EXISTS training_check_in (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    plan_id BIGINT NOT NULL COMMENT '计划ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    check_in_date DATE NOT NULL COMMENT '打卡日期',
    week_number INT NOT NULL COMMENT '第几周',
    day_of_week INT NOT NULL COMMENT '周几(1-7)',
    exercise_type VARCHAR(50) COMMENT '运动类型',
    duration INT COMMENT '运动时长(分钟)',
    completed BOOLEAN DEFAULT TRUE COMMENT '是否完成',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_plan_date (plan_id, check_in_date),
    INDEX idx_user_id (user_id),
    INDEX idx_check_in_date (check_in_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='训练打卡记录表';
