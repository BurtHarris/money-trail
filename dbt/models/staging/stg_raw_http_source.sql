{{ config(materialized='view') }}

select
  fetched_at,
  url,
  status_code,
  length(content_preview) as preview_length
from raw_http_source
