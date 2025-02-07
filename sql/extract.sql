-- First get all LearnDash courses with their metadata
WITH course_data AS (
    SELECT 
        p.ID as course_id,
        p.post_title as display_name,
        p.post_content as definition_data,
        p.post_status as status,
        p.post_modified as edited_on,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = '_sfwd-courses' THEN pm.meta_value
                ELSE NULL 
            END
        ) as course_settings,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = 'course_points' THEN pm.meta_value
                ELSE NULL 
            END
        ) as course_points
    FROM wp_posts p
    LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id
    WHERE p.post_type = 'sfwd-courses'
    GROUP BY p.ID
),

-- Get lessons data
lesson_data AS (
    SELECT 
        p.ID as lesson_id,
        p.post_parent as course_id,
        p.post_title as display_name,
        p.post_content as definition_data,
        p.menu_order as sort_order,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = 'course_id' THEN pm.meta_value
                ELSE NULL 
            END
        ) as linked_course_id,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = '_sfwd-lessons' THEN pm.meta_value
                ELSE NULL 
            END
        ) as lesson_settings
    FROM wp_posts p
    LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id
    WHERE p.post_type = 'sfwd-lessons'
    GROUP BY p.ID
),

-- Get topics data
topic_data AS (
    SELECT 
        p.ID as topic_id,
        p.post_parent as lesson_id,
        p.post_title as display_name,
        p.post_content as definition_data,
        p.menu_order as sort_order,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = 'course_id' THEN pm.meta_value
                ELSE NULL 
            END
        ) as linked_course_id,
        GROUP_CONCAT(
            CASE 
                WHEN pm.meta_key = '_sfwd-topic' THEN pm.meta_value
                ELSE NULL 
            END
        ) as topic_settings
    FROM wp_posts p
    LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id
    WHERE p.post_type = 'sfwd-topic'
    GROUP BY p.ID
)
-- Final export query combining all data
SELECT 
    c.*,
    JSON_OBJECT(
        'lessons', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'id', l.lesson_id,
                    'display_name', l.display_name,
                    'definition_data', l.definition_data,
                    'sort_order', l.sort_order,
                    'settings', l.lesson_settings,
                    'topics', (
                        SELECT JSON_ARRAYAGG(
                            JSON_OBJECT(
                                'id', t.topic_id,
                                'display_name', t.display_name,
                                'definition_data', t.definition_data,
                                'sort_order', t.sort_order,
                                'settings', t.topic_settings
                            )
                        )
                        FROM topic_data t
                        WHERE t.lesson_id = l.lesson_id
                    )
                    
                )
            )
            FROM lesson_data l
            WHERE l.linked_course_id = c.course_id
        )
    ) as course_structure
FROM course_data c;