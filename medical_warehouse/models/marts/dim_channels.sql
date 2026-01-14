with base_channels as (
    select 
        channel_name,
        min(message_timestamp) as first_post_date,
        max(message_timestamp) as last_post_date,
        count(*) as total_posts,
        avg(view_count) as avg_views
    from {{ ref('stg_telegram_messages') }}
    group by 1
)

select
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name,
    case 
        when channel_name in ('CheMed123', 'tikvahpharma', 'LiyuPharma') then 'Medical/Pharma'
        when channel_name in ('lobelia4cosmetics') then 'Cosmetics'
        else 'Health'
    end as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from base_channels
