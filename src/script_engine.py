from google import genai
from google.cloud import bigquery


class SiteGroundScriptEngine:
    """
    Scripting and Telemetry Engine.
    Queries Performance Max analytics from BigQuery and uses Gemini 3.5 Flash
    to synthesize performance-optimized ad copy.
    """

    def __init__(self):
        self.client = genai.Client()
        self.bq_client = bigquery.Client()
        self.script_model = "gemini-3.5-flash"

    def fetch_pmax_telemetry(self, campaign_category: str) -> str:
        """Fetch past top-performing campaign hooks from BigQuery."""
        try:
            query = """
                SELECT hook_text, avg_ctr, conversion_rate
                FROM `siteground_analytics.pmax_creative_telemetry`
                WHERE category = %s
                ORDER BY conversion_rate DESC LIMIT 3
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(None, "STRING", campaign_category)
                ]
            )
            query_job = self.bq_client.query(query, job_config=job_config)
            results = query_job.result()

            telemetry_lines = []
            for r in results:
                telemetry_lines.append(
                    f'- Hook: "{r.hook_text}" (CTR: {r.avg_ctr:.2%}, Conv: {r.conversion_rate:.2%})'
                )

            if not telemetry_lines:
                return "Default hook strategy: Focus on SiteGround speed, security, and 24/7 technical support."
            return "\n".join(telemetry_lines)

        except Exception as e:
            # Safe degradable fallback if credentials or table are missing
            print(f"QUERY ERROR: {e}")
            return "Default hook strategy: Focus on SiteGround speed, security, and 24/7 technical support."

    def generate_scripts(self, prompt: str, category: str) -> str:
        """Synthesize conversion-optimized scripts based on prompt and past telemetry."""
        telemetry_context = self.fetch_pmax_telemetry(category)

        prompt_instruction = (
            f"Historical top performers:\n{telemetry_context}\n\n"
            f"Task: Generate 3 ad scripts with SSML tags for campaign brief: {prompt}"
        )

        resp = self.client.models.generate_content(
            model=self.script_model, contents=[prompt_instruction]
        )
        return resp.text
