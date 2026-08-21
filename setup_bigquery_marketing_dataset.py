import os
from google.cloud import bigquery

PROJECT_ID = "firsttestproject-343414"
DATASET_ID = "siteground_marketing_analytics"

def setup_marketing_analytics_dataset():
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    
    # 1. Create Dataset if not exists
    try:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset.description = "Synthetic Marketing Studio Telemetry, PMax Creative Performance & Segment Cohorts"
        client.create_dataset(dataset, exists_ok=True)
        print(f"✅ Dataset {PROJECT_ID}.{DATASET_ID} verified/created.")
    except Exception as e:
        print(f"Error creating dataset: {e}")

    # 2. Table: pmax_creative_telemetry
    table_ref_pmax = dataset_ref.table("pmax_creative_telemetry")
    schema_pmax = [
        bigquery.SchemaField("hook_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("hook_text", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_audience", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("avg_ctr", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("conversion_rate", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("cpa_dollars", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("abcd_quality_score", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("search_query_cluster", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("best_performing_palette", "STRING", mode="NULLABLE"),
    ]
    table_pmax = bigquery.Table(table_ref_pmax, schema=schema_pmax)
    client.create_table(table_pmax, exists_ok=True)
    print("✅ Table pmax_creative_telemetry verified/created.")

    # 3. Populate pmax_creative_telemetry
    rows_pmax = [
        {
            "hook_id": "HK-101",
            "hook_text": "Is your slow website killing your sales? 1-second delay = 7% conversion loss.",
            "category": "managed_wordpress",
            "target_audience": "WooCommerce & E-Commerce Store Owners",
            "avg_ctr": 0.0884,
            "conversion_rate": 0.1420,
            "cpa_dollars": 14.50,
            "abcd_quality_score": 9.7,
            "search_query_cluster": "slow wordpress site checkout fix",
            "best_performing_palette": "Signature Brand Green"
        },
        {
            "hook_id": "HK-102",
            "hook_text": "Stop paying $200/mo for sluggish cloud hosting. Switch to SiteGround Ultra NVMe.",
            "category": "cloud_hosting",
            "target_audience": "Digital Agencies & Web Developers",
            "avg_ctr": 0.0842,
            "conversion_rate": 0.1280,
            "cpa_dollars": 18.20,
            "abcd_quality_score": 9.5,
            "search_query_cluster": "best fast agency cloud hosting 2026",
            "best_performing_palette": "Deep Obsidian & Emerald"
        },
        {
            "hook_id": "HK-103",
            "hook_text": "It's 2 AM and your site is DOWN. SiteGround 24/7 technical experts reply in 2 seconds.",
            "category": "enterprise_support",
            "target_audience": "SMB Business Owners & Founders",
            "avg_ctr": 0.0805,
            "conversion_rate": 0.1190,
            "cpa_dollars": 21.00,
            "abcd_quality_score": 9.6,
            "search_query_cluster": "reliable 24 7 wordpress support hosting",
            "best_performing_palette": "Clean Studio White"
        },
        {
            "hook_id": "HK-104",
            "hook_text": "Accelerate your PageSpeed score to 100/100 with SuperCacher 3-layer acceleration.",
            "category": "managed_wordpress",
            "target_audience": "SEO Professionals & Growth Marketers",
            "avg_ctr": 0.0792,
            "conversion_rate": 0.1140,
            "cpa_dollars": 16.80,
            "abcd_quality_score": 9.4,
            "search_query_cluster": "core web vitals 100 100 wordpress",
            "best_performing_palette": "Signature Brand Green"
        },
        {
            "hook_id": "HK-105",
            "hook_text": "Limited Time Special Offer: 80% Off Managed Cloud Hosting + Free Migration & SSL.",
            "category": "promotional_discount",
            "target_audience": "Bargain Seekers & New Site Launchers",
            "avg_ctr": 0.0915,
            "conversion_rate": 0.1550,
            "cpa_dollars": 11.20,
            "abcd_quality_score": 9.8,
            "search_query_cluster": "siteground 80 discount promo code",
            "best_performing_palette": "High-Contrast Emerald"
        }
    ]
    
    # Overwrite / insert clean synthetic records
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.pmax_creative_telemetry` WHERE true").result()
    errors_pmax = client.insert_rows_json(table_pmax, rows_pmax)
    if not errors_pmax:
        print(f"✅ Loaded {len(rows_pmax)} synthetic PMax creative telemetry rows.")
    else:
        print("PMax insert errors:", errors_pmax)

    # 4. Table: customer_cohorts_ltv
    table_ref_cohorts = dataset_ref.table("customer_cohorts_ltv")
    schema_cohorts = [
        bigquery.SchemaField("cohort_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("cohort_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("region", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("avg_ltv_usd", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("churn_risk", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("opportunity_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("recommended_hook", "STRING", mode="NULLABLE"),
    ]
    table_cohorts = bigquery.Table(table_ref_cohorts, schema=schema_cohorts)
    client.create_table(table_cohorts, exists_ok=True)
    print("✅ Table customer_cohorts_ltv verified/created.")

    rows_cohorts = [
        {
            "cohort_id": "COH-EMEA-DEV",
            "cohort_name": "EMEA Developer & Freelance Agencies",
            "region": "EMEA",
            "avg_ltv_usd": 1450.00,
            "churn_risk": "Low (4.2%)",
            "opportunity_score": 94.5,
            "recommended_hook": "Git integration, staging environments, WP-CLI automation"
        },
        {
            "cohort_id": "COH-US-ECOM",
            "cohort_name": "US High-Traffic WooCommerce Stores",
            "region": "North America",
            "avg_ltv_usd": 2890.00,
            "churn_risk": "Medium (8.1%)",
            "opportunity_score": 96.0,
            "recommended_hook": "3X speed boost, zero checkout downtime, Black Friday scale"
        },
        {
            "cohort_id": "COH-APAC-SMB",
            "cohort_name": "APAC Growing SMB Creators",
            "region": "APAC",
            "avg_ltv_usd": 720.00,
            "churn_risk": "Low (5.0%)",
            "opportunity_score": 88.0,
            "recommended_hook": "80% Off starter promotion + 24/7 instant chat support"
        }
    ]
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.customer_cohorts_ltv` WHERE true").result()
    errors_cohorts = client.insert_rows_json(table_cohorts, rows_cohorts)
    if not errors_cohorts:
        print(f"✅ Loaded {len(rows_cohorts)} synthetic customer cohort LTV rows.")
    else:
        print("Cohort insert errors:", errors_cohorts)

    # 5. Table: competitor_benchmarks
    table_ref_comp = dataset_ref.table("competitor_benchmarks")
    schema_comp = [
        bigquery.SchemaField("competitor_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("weakness_angle", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("benchmark_ttfb_ms", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("siteground_ttfb_ms", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("counter_narrative_hook", "STRING", mode="REQUIRED"),
    ]
    table_comp = bigquery.Table(table_ref_comp, schema=schema_comp)
    client.create_table(table_comp, exists_ok=True)
    print("✅ Table competitor_benchmarks verified/created.")

    rows_comp = [
        {
            "competitor_name": "Bluehost / Generic EIG",
            "weakness_angle": "Slow shared server response times and sluggish backend",
            "benchmark_ttfb_ms": 1280,
            "siteground_ttfb_ms": 190,
            "counter_narrative_hook": "Tired of waiting 2 seconds for your dashboard to load? Experience 190ms TTFB on SiteGround Google Cloud servers."
        },
        {
            "competitor_name": "GoDaddy",
            "weakness_angle": "Aggressive upsells for basic SSL & security features",
            "benchmark_ttfb_ms": 950,
            "siteground_ttfb_ms": 190,
            "counter_narrative_hook": "Stop paying extra for basic SSL certificates and daily backups. Get enterprise security included for free."
        },
        {
            "competitor_name": "WP Engine",
            "weakness_angle": "Extremely high price points ($300+/yr) for entry-level limits",
            "benchmark_ttfb_ms": 320,
            "siteground_ttfb_ms": 190,
            "counter_narrative_hook": "Get identical high-performance managed cloud speed at 1/3 the cost of premium hosting."
        }
    ]
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.competitor_benchmarks` WHERE true").result()
    errors_comp = client.insert_rows_json(table_comp, rows_comp)
    if not errors_comp:
        print(f"✅ Loaded {len(rows_comp)} competitor benchmark rows.")
    else:
        print("Competitor insert errors:", errors_comp)

    print(f"\n🎉 ALL SYNTHETIC BIGQUERY DATASETS & TABLES CREATED ON {PROJECT_ID}.{DATASET_ID}!")

if __name__ == "__main__":
    setup_marketing_analytics_dataset()
