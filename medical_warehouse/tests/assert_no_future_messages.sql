-- Custom test to ensures no messages have future dates
select *
from {{ ref('stg_telegram_messages') }}
where message_timestamp > current_timestamp
