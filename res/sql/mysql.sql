CREATE TABLE needle_store (  
    index_id BIGINT AUTO_INCREMENT,  
    index_name VARCHAR(100) NOT NULL,  
    PRIMARY KEY (index_id),  
    UNIQUE KEY unique_index_name (index_name)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;