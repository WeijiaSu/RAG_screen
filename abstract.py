import pandas as pd
import time
import csv
from playwright.sync_api import sync_playwright, TimeoutError
import re

def extract_info_from_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        page.goto(url, wait_until="networkidle")  # wait for JS-heavy SPAs

        # Wait a bit longer for JS content to populate
        page.wait_for_timeout(10000)
        full_text = page.locator("body").inner_text()
        browser.contexts[0].pages[0].bring_to_front()
        #print(full_text)
        browser.close()
        #print(full_text)
    return full_text

def parse_info(full_text):
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    title_line = next((line for line in lines if re.match(r"\d+\s*/\s*\d+\s*-", line)), "")
    title = title_line.strip()

    presenter_line = next((line for line in lines if "University" in line or "Institute" in line), "")
    match = re.match(r"(?P<name>.+?)\. (?P<affiliation>.+)", presenter_line)
    presenter = match.group("name").strip() if match else ""
    affiliation = match.group("affiliation").strip() if match else ""

    abstract_lines = []
    found_abstract = False
    for line in lines:
        if found_abstract:
            if line.startswith(("AACR Annual Meeting", "Citation", "Questions?")):
                break
            abstract_lines.append(line)
        elif line == "Abstract":
            found_abstract = True
    abstract = " ".join(abstract_lines).strip()

    return presenter, affiliation, title, abstract

# # === Main loop ===
# df = pd.read_excel("./2025_Leads.xlsx")  # Replace with actual file
# output_file = "./abstract_info_output.csv"
# error_file = "./failed_urls.csv"
# pd.set_option("display.max_column",40)
# print(df[0:10])
# df=df.loc[df["Poster Number"].notna()]
# print(df[0:10])

# # Trackers
# total = len(df)
# success = 0
# fail = 0
# start_time = time.time()
# failed_urls = []

# with open(output_file, mode="w", newline="", encoding="utf-8") as fout:
#     writer = csv.writer(fout)
#     writer.writerow(["URL", "Presenter", "Affiliation", "Title", "Abstract"])

#     for idx, row in df.iterrows():
#         url = row.get("Abstract Link")
#         try:
#             print(f"⏳ [{idx+1}/{total}] Processing: {url}")
#             full_text = extract_info_from_url(url)
#             presenter, affiliation, title, abstract = parse_info(full_text)
#             writer.writerow([url, presenter, affiliation, title, abstract])
#             success += 1
#         except Exception as e:
#             print(f"❌ Error at row {idx+1}: {e}")
#             failed_urls.append(url)
#             fail += 1
#         finally:
#             elapsed = time.time() - start_time
#             print(f"✅ Success: {success} | ❌ Fail: {fail} | ⏱️ Elapsed: {elapsed:.1f}s\n")

# # Save failed URLs if needed
# if failed_urls:
#     pd.DataFrame({"Failed URL": failed_urls}).to_csv(error_file, index=False)
#     print(f"🔺 Failed URLs saved to {error_file}")


# === Main loop ===
df = pd.read_csv("./failed_urls2.csv",header=None) 
output_file = "./abstract_info_output3.csv"
error_file = "./failed_urls3.csv"
pd.set_option("display.max_column",40)
print(df[0:10])
print(df.shape)


# # Trackers
total = len(df)
success = 0
fail = 0
start_time = time.time()
failed_urls = []

with open(output_file, mode="w", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout)
    writer.writerow(["URL", "Presenter", "Affiliation", "Title", "Abstract"])

    for idx, row in df.iterrows():
        url = row.get(0)
        try:
            print(f"⏳ [{idx+1}/{total}] Processing: {url}")
            full_text = extract_info_from_url(url)
            presenter, affiliation, title, abstract = parse_info(full_text)

            if not abstract.strip():
                raise ValueError("Empty abstract")

            writer.writerow([url, presenter, affiliation, title, abstract])
            success += 1

        except Exception as e:
            print(f"❌ Error at row {idx+1}: {e}")
            failed_urls.append(url)
            fail += 1

        finally:
            elapsed = time.time() - start_time
            print(f"✅ Success: {success} | ❌ Fail: {fail} | ⏱️ Elapsed: {elapsed:.1f}s\n")

# Save failed URLs if needed
if failed_urls:
    pd.DataFrame({"Failed URL": failed_urls}).to_csv(error_file, index=False)
    print(f"🔺 Failed URLs saved to {error_file}")
