-- All candidates financial summary staging model
-- Cleans and aliases raw FEC all-candidates summary data

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cand_id,
      cand_name,
      cand_ici,
      pty_cd,
      cand_pty_affiliation,
      try_cast(nullif(trim(ttl_receipts), '') as decimal(14,2)) as ttl_receipts,
      try_cast(nullif(trim(trans_from_auth), '') as decimal(14,2)) as trans_from_auth,
      try_cast(nullif(trim(ttl_disb), '') as decimal(14,2)) as ttl_disb,
      try_cast(nullif(trim(trans_to_auth), '') as decimal(14,2)) as trans_to_auth,
      try_cast(nullif(trim(coh_bop), '') as decimal(14,2)) as coh_bop,
      try_cast(nullif(trim(coh_cop), '') as decimal(14,2)) as coh_cop,
      try_cast(nullif(trim(cand_contrib), '') as decimal(14,2)) as cand_contrib,
      try_cast(nullif(trim(cand_loans), '') as decimal(14,2)) as cand_loans,
      try_cast(nullif(trim(other_loans), '') as decimal(14,2)) as other_loans,
      try_cast(nullif(trim(cand_loan_repay), '') as decimal(14,2)) as cand_loan_repay,
      try_cast(nullif(trim(other_loan_repay), '') as decimal(14,2)) as other_loan_repay,
      try_cast(nullif(trim(debts_owed_by), '') as decimal(14,2)) as debts_owed_by,
      try_cast(nullif(trim(ttl_indiv_contrib), '') as decimal(14,2)) as ttl_indiv_contrib,
      cand_office_st,
      cand_office_district,
      spec_election,
      prim_election,
      run_election,
      gen_election,
      try_cast(nullif(trim(gen_election_precent), '') as decimal(7,4)) as gen_election_precent,
      try_cast(nullif(trim(other_pol_cmte_contrib), '') as decimal(14,2)) as other_pol_cmte_contrib,
      try_cast(nullif(trim(pol_pty_contrib), '') as decimal(14,2)) as pol_pty_contrib,
      coalesce(
        cast(try_strptime(nullif(trim(cvg_end_dt), ''), '%m/%d/%Y') as date),
        cast(try_strptime(nullif(trim(cvg_end_dt), ''), '%m%d%Y') as date)
      ) as cvg_end_dt,
      try_cast(nullif(trim(indiv_refunds), '') as decimal(14,2)) as indiv_refunds,
      try_cast(nullif(trim(cmte_refunds), '') as decimal(14,2)) as cmte_refunds,
      {{ cycle }} as cycle
    from raw.weball_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
