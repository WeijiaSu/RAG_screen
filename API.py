from openai import OpenAI
import pandas as pd
import csv
import time
import math


with open("product_description.txt", "r") as f:
    product_summary = f.read()

system_prompt = f"""

{product_summary}


"""

client = OpenAI()

def format_batch(rows):
    lines = []
    for _, row in rows.iterrows():
        lines.append(f"Organization: {row['Organisation']}\nAbstract: {row['Abstract']}\nURL: {row['URL']}")
    return "\n\n".join(lines)


def get_batch_scores(batch_rows):
    user_prompt = f"""
Here are the 20 attendees:

{format_batch(batch_rows)}

Please return a 20-line response with the format: <URL>, <score>, <reason>
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error:", e)
        return "ERROR"

all_outputs = []

start_time = time.time()

# Loop over DataFrame in batches of 20
res=pd.read_csv("filter.keyword.csv",quoting=csv.QUOTE_ALL)
df=res
batch_size = 20
for i in range(0, len(df), batch_size):
    elapsed = time.time() - start_time
    batch = df.iloc[i:i + batch_size]
    print(f"Processing batch {i // batch_size + 1} out of {math.ceil(len(df)/batch_size)} batches elapsed: {elapsed:.1f}s\n")
    result_text = get_batch_scores(batch)
    all_outputs.append(result_text)
    time.sleep(2)  # delay to avoid rate limits

end_time = time.time()
print(f"Running time: {end_time - start_time:.4f} seconds")


# Save to text file
with open("gpt_batch_scores_round2.txt", "w") as f:
    f.write("\n\n".join(all_outputs))

print("Done! Scores saved to gpt_batch_scores.txt")
