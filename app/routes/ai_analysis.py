import os
import json
from openai import OpenAI



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




def get_keywords_and_competitors(domain):
    prompt = """
    I will provide a domain name. Based on that domain, return a JSON object with exactly two elements. Your response must be consistent and deterministic — do not vary results between repeated calls with the same input.
    
    1. 'list_of_keywords' — return exactly 10 relevant, SEO-friendly keywords that are evergreen and directly related to the domain's niche. These keywords should be selected based on the domain’s content and focus, not on trending or time-sensitive data.
    
    2. 'list_of_compitator_links' — return exactly 10 direct URLs (homepages) of top competitors for this domain. Base this on organic search similarity, content overlap, and target audience — and keep the output consistent for this domain every time.
    
    The output should be in the following strictJSON format:
    
    {{"list_of_keywords": [ "keyword1", "keyword2", "keyword3", ..., "keyword10" ],
    "list_of_compitator_links": [ "competitor1", "competitor2", ..., "competitor10" ]}}
    
    Now, here is the domain: {DOMAIN}. Make sure to return the response in the exact JSON format as shown above, and don't add any other extra characters or spaces.
    """
    prompt = prompt.format(DOMAIN=domain)

    response = client.responses.create(
    model="gpt-4.1",
    input=prompt,
    temperature=0
    )

    # print(response.output[0].content[0].text)
    response = json.loads(response.output[0].content[0].text)

    return response