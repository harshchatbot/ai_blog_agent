from tools.image_tools import generate_featured_image_raw

def main():
    prompt = (
        "Minimal flat illustration of Salesforce automation with Flow diagrams, "
        "cloud icons, and business users collaborating. Clean modern blog featured image."
    )

    img_b64 = generate_featured_image_raw(prompt)
    print("Type:", type(img_b64))
    print("Length:", len(img_b64))
    print("Preview:", str(img_b64)[:200])

if __name__ == "__main__":
    main()
