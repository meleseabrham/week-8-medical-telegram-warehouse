select
    id,
    channel,
    content,
    timestamp
from {{ source('public', 'raw_messages') }}
