-- BigQuery Schema Setup for Manuel El Manual
-- Run this in the BigQuery console to create the required tables

-- 1. Create the dataset (schema)
CREATE SCHEMA IF NOT EXISTS manuals_dataset
  OPTIONS (
    description = "Manuel El Manual - Internal manuals management system"
  );

-- 2. Create manuals_dict table (main manual metadata)
CREATE TABLE IF NOT EXISTS manuals_dataset.manuals_dict (
  manual_id STRING NOT NULL OPTIONS(description="Unique manual identifier, e.g., MAN-abc123"),
  title STRING OPTIONS(description="Manual title"),
  business_area STRING OPTIONS(description="Business area or department"),
  requester STRING OPTIONS(description="Person who requested this manual"),
  created_by STRING OPTIONS(description="Creator name or email"),
  created_at TIMESTAMP OPTIONS(description="Creation timestamp"),
  last_updated TIMESTAMP OPTIONS(description="Last update timestamp"),
  context STRING OPTIONS(description="Manual context and objective"),
  requirements STRING OPTIONS(description="Prerequisites and requirements"),
  permissions STRING OPTIONS(description="Required permissions and access"),
  outputs STRING OPTIONS(description="Expected outputs and deliverables"),
  keywords ARRAY<STRING> OPTIONS(description="Search keywords/tags")
)
OPTIONS(
  description = "Main table storing manual metadata and dictionary information"
);

-- 3. Create manual_steps table (procedure steps)
CREATE TABLE IF NOT EXISTS manuals_dataset.manual_steps (
  manual_id STRING NOT NULL OPTIONS(description="Foreign key to manuals_dict"),
  step_number INT64 OPTIONS(description="Step sequence number"),
  step_title STRING OPTIONS(description="Step title"),
  step_description STRING OPTIONS(description="Detailed step description"),
  expected_output STRING OPTIONS(description="Expected result from this step"),
  required_tools STRING OPTIONS(description="Tools or systems needed"),
  estimated_time STRING OPTIONS(description="Estimated time to complete"),
  is_critical BOOL OPTIONS(description="Whether this is a critical step")
)
OPTIONS(
  description = "Table storing step-by-step procedures for each manual"
);

-- 4. Create manual_files table (file versions)
CREATE TABLE IF NOT EXISTS manuals_dataset.manual_files (
  manual_id STRING NOT NULL OPTIONS(description="Foreign key to manuals_dict"),
  version INT64 OPTIONS(description="File version number"),
  file_path STRING OPTIONS(description="GCS path to the file, e.g., gs://bucket/path"),
  format STRING OPTIONS(description="File format, e.g., html, pdf, markdown"),
  created_at TIMESTAMP OPTIONS(description="File creation timestamp"),
  created_by STRING OPTIONS(description="User who created this version")
)
OPTIONS(
  description = "Table storing file versions and their GCS locations"
);

-- Optional: Create indexes for better query performance
-- Note: BigQuery doesn't have traditional indexes, but clustering helps

-- Verify tables were created
SELECT 
  table_name, 
  row_count,
  size_bytes / 1024 / 1024 as size_mb
FROM `manuals_dataset.__TABLES__`;
