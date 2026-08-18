import os
import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPOS = [
    "pandas-dev/pandas",
    "apache/airflow",
    "ShilaThapa/elt-github-api-pipeline"
]

def fetch_repo_metadata(owner_repo):
    url = f"https://api.github.com/repos/{owner_repo}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

def insert_repo(cursor, data):
    cursor.execute(
        """
        INSERT INTO REPOS (full_name, stargazers_count, forks_count, language, open_issues_count, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            data["full_name"],
            data["stargazers_count"],
            data["forks_count"],
            data["language"],
            data["open_issues_count"],
            data["created_at"],
        )
    )

if __name__ == "__main__":
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    for repo in REPOS:
        data = fetch_repo_metadata(repo)
        insert_repo(cursor, data)
        print(f"Inserted: {data['full_name']}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Done. Data loaded into Snowflake.")