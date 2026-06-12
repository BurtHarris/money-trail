# FEC Data Staging Models Reference

This guide maps each staging model to the official FEC file format documentation and describes the normalization applied.

## File Type Reference

| File Type | Code | Staging Model | FEC Documentation | Description |
|-----------|------|---------------|--------------------|-------------|
| Individual Contributions | indiv | `stg_indiv` | [Link](https://www.fec.gov/campaign-finance-data/individual-contributions-file-description/) | Individual donor contributions |
| Candidate Master | cn | `stg_cn` | [Link](https://www.fec.gov/campaign-finance-data/candidate-master-file-description/) | Candidate details (name, party, office) |
| Committee Master | cm | `stg_cm` | [Link](https://www.fec.gov/campaign-finance-data/committee-master-file-description/) | Committee details (name, designation, type) |
| Candidate-Committee Linkage | ccl | `stg_ccl` | [Link](https://www.fec.gov/campaign-finance-data/candidate-committee-linkage-file-description/) | Links between candidates and committees |
| Committee-to-Committee Transfers | oth | `stg_oth` | [Link](https://www.fec.gov/campaign-finance-data/committee-to-committee-transfers-file-description/) | Committee-to-committee transactions |
| Contributions to Candidates | pas2 | `stg_pas2` | [Link](https://www.fec.gov/campaign-finance-data/contributions-candidates-file-description/) | Committee contributions to candidates |
| Operating Expenditures | oppexp | `stg_oppexp` | [Link](https://www.fec.gov/campaign-finance-data/operating-expenditures-file-description/) | Committee operating expenses |
| All Candidates Financial Summary | weball | `stg_weball` | [Link](https://www.fec.gov/campaign-finance-data/all-candidates-file-description/) | Aggregate candidate financial summaries |

## Normalization Rules

All staging models apply the following normalization:

### Text Fields
- **Whitespace**: All text fields are trimmed (leading/trailing spaces removed)
- **Case**: Original FEC case is preserved (no case conversion)
- **Length**: Handled by DuckDB VARCHAR type (no truncation except where noted)

### Numeric Fields
- **Amounts** (DECIMAL): Rounded to 2 decimal places (cents)
- **ZIP Codes** (VARCHAR): Truncated to 5 digits using `LEFT(trim(zip_code), 5)`
- **IDs**: Converted to appropriate types (BIGINT for file/sub numbers, VARCHAR for text IDs)

### Dates
- **Format**: FEC dates are typically `MMDDYYYY` or `MM/DD/YYYY`
- **Parsing**: Parsed using `TRY_STRPTIME()` with fallback to NULL on parse error
- **Type**: Converted to DATE

### NULL Handling
- **Empty Strings**: Converted to NULL using `NULLIF(TRIM(field), '')`
- **Invalid Values**: Invalid type conversions return NULL via `TRY_CAST()`

## Adding New File Types

To add a new FEC file type (e.g., `indexp`):

1. Create `dbt/models/staging/stg_<file_type>.sql` following the pattern of existing models
2. Define the schema in the model's SELECT statement with FEC column names
3. Apply normalization (trim, type-cast, date parsing) per the rules above
4. Add test entries to `dbt/models/staging/staging.yml`
5. Update this reference guide

## Testing

Each staging model includes dbt tests defined in `staging.yml`:

- **Uniqueness**: Primary key fields (e.g., `tran_id`, `cmte_id`)
- **Not Null**: Critical fields that should always be populated
- **Domain**: ZIP codes limited to 5 digits or NULL
- **Accepted Values**: Enum fields (e.g., cycles, office types)

Run tests with:
```bash
cd dbt
dbt test --select tag:staging
```

## Data Quality Notes

- **Cycles**: Staging models union cycles [2024, 2022, 2020]. Adjust in model code if importing additional cycles.
- **Duplicates**: Some FEC files intentionally contain duplicates (amendments, amendments to amendments). dbt tests document expected uniqueness constraints.
- **Referential Integrity**: Linkages (CCL joining candidates to committees) are validated in marts models.
