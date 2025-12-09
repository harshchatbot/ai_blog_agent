from pathlib import Path
from tools.cms_tools import post_to_wordpress_raw

def main():
    # 1) Metadata from your Crew output
    title = "Salesforce Flow vs Process Builder in 2025: Which Automation Tool Should You Use?"
    slug = "salesforce-flow-vs-process-builder-2025"
    excerpt = (
        "Compare Salesforce Flow vs Process Builder in 2025. Learn about their differences, "
        "Salesforce's plan to retire Process Builder, and best practices to migrate to Flow for "
        "future-proof automation."
    )

    # 2) Load HTML content from file
    html_path = Path("data/manual_posts/flow-vs-process-builder-2025.html")
    content_html = html_path.read_text(encoding="utf-8")

    print("📄 Loaded HTML content from:", html_path)

    # 3) Call the same WordPress tool we wired for CrewAI
    print("📨 Sending post to WordPress as draft...")
    res = post_to_wordpress_raw(
    title=title,
    content=content_html,
    slug=slug,
    excerpt=excerpt,
    )



    print("✅ WordPress API response:")
    print(res)


if __name__ == "__main__":
    main()
