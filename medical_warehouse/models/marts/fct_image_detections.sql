with detections as (
    select * from {{ source('raw', 'yolo_detections') }}
),

messages as (
    select * from {{ ref('fct_messages') }}
),

dim_channels as (
    select * from {{ ref('dim_channels') }}
),

dim_dates as (
    select * from {{ ref('dim_dates') }}
)

select
    d.id as detection_id,
    d.message_id,
    d.channel_name,
    c.channel_key,
    m.date_key,
    d.image_path,
    d.primary_class,
    d.confidence_score,
    d.image_category,
    d.detection_date
from detections d
left join messages m on d.message_id = m.message_id
left join dim_channels c on d.channel_name = c.channel_name
-- Join/Scan date key based on message timestamp matching not needed if we join fct_messages which has date_key
