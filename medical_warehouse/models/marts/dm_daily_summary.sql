select
    channel,
    date(timestamp) as event_date,
    count(*) as message_count
from {{ ref('stg_messages') }}
group by 1, 2
