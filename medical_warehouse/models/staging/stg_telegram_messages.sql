with raw_data as (
    select * from {{ source('raw', 'telegram_messages') }}
),

cleaned_data as (
    select
        message_id,
        channel_name,
        cast(message_date as timestamp) as message_timestamp,
        message_text,
        case when message_text is null or message_text = '' then true else false end as is_empty,
        coalesce(views, 0) as view_count,
        coalesce(forwards, 0) as forward_count,
        has_media as has_image,
        image_path,
        length(message_text) as message_length
    from raw_data
    where message_id is not null
)

select * from cleaned_data
where not is_empty
