import boto3
import json
import urllib.parse
import random
import base64
import time
import os
from google import genai
from PIL import Image
from io import BytesIO
import requests

# model = "amazon"
# model = "google"
model = os.environ.get('MODEL_NAME') 
#From github actions
# PROMPTS = {
#     "clothing": {
#         "image_prompt": "A high-quality kids clothing product photo with soft pastel background, studio lighting",
#         "description_prompt": "Generate a product description for the kids clothing item shown in the image I only have three category of kids clothing party wear dresses, co-ord sets & nightsuits, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
#         "title_prompt": "Generate a product title for the kids clothing item shown in the image I only have three category of kids clothing party wear dresses, co-ord sets & nightsuits, do a deep anylsis on the design before giving the title for website listing, make sure the title is under 6 words and dont return anything else only prodouct title. Return product title as plain text (no markdown, no formatting)"
#     },
#     "accessories": {
#         "image_prompt": "Minimal premium accessory product shot with white background",
#         "description_prompt": "Generate a product description for the kids accessory item shown in the image, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
#         "title_prompt": "Generate a product title for the kids accessories item shown in the image, do a deep anylsis on the design and give a title for website listing make sure the title is under 6 words and dont return anything else only prodouct title. Return product title as plain text (no markdown, no formatting)"
#     },
#     "footwear": {
#         "image_prompt": "Stylish kids footwear product photo with clean background",
#         "description_prompt": "Generate a product description for the kids footwear item shown in the image, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
#         "title_prompt": "Generate a product title for the kids footwear item shown in the image, do a deep anylsis on the design and give a title for website listing make sure the title is under 6 words and dont return anything else only prodouct title. Return product title as plain text (no markdown, no formatting)"
#     }
# }
PROMPTS = {
    "clothing": {
        "image_prompt": "A high-quality kids clothing product photo with soft pastel background, studio lighting",
        "description_prompt": "You are an expert e-commerce copywriter specializing in kids' fashion. Analyze the provided product image carefully and generate a high-quality, accurate, and engaging product description for a kids' clothing item. First, identify the correct category strictly from these three options only: Party Wear Dress, Co-ord Set, or Nightsuit. Then perform a deep visual analysis of the product including fabric type (estimate if not obvious), colors, patterns, prints, embroidery, design elements such as frills, bows, collars, buttons, lace, or elastic, fit and silhouette, sleeve type and length, neck style, seasonal suitability, and overall comfort for kids. Based on this, generate a Product Title in plain text only without any symbols, formatting, or markdown, ensuring it is SEO-friendly and includes key attributes like color, type, and style. Then write a Product Description in 2 or 3 short paragraphs highlighting style, comfort, and use-case such as party wear, sleepwear, or casual wear, focusing on benefits for both kids and parents. After that, include Key Features written inline in a single paragraph separated by hyphens, covering aspects like fabric feel, comfort, durability, design appeal, and occasion suitability. Use simple, premium, and persuasive language that sounds natural and human-like, avoid over-claiming or adding unverifiable details, and if any attribute is unclear from the image, use neutral terms such as soft fabric instead of guessing. The final output should be clean, structured, and ready to upload to an e-commerce store with strong conversion potential.",
        "title_prompt": "You are an expert e-commerce copywriter for kids' fashion. Analyze the provided product image carefully and identify the correct category strictly from these three options only: Party Wear Dress, Co-ord Set, or Nightsuit. Perform a deep visual analysis of the design, including color, pattern, style elements, and overall look before generating the title. Create a concise, SEO-friendly product title suitable for an e-commerce website that clearly reflects the products key attributes such as color, style, and category. The title must be under 6 words, natural-sounding, and appealing for online shoppers. Do not include any extra words, explanations, symbols, or formatting. Return only the product title as plain text."
    },
    "accessories": {
        "image_prompt": "Minimal premium accessory product shot with white background",
        "description_prompt": "You are an expert e-commerce copywriter specializing in kids' accessories. Analyze the provided product image carefully and perform a deep visual analysis of the item, including its type (such as hairband, clips, cap, socks, bag, etc.), material (estimate if not obvious), colors, patterns, textures, design elements, size appearance, and overall style. Based on this, generate a high-quality and accurate product listing. First, create a Product Title in plain text only without any symbols, formatting, or markdown, ensuring it is concise, SEO-friendly, and clearly reflects key attributes like color, style, and product type. Then write a Product Description in 2 or 3 short paragraphs highlighting design, comfort, usability, durability, and appeal for kids, focusing on both style and practicality for parents. After that, include Key Features written in a single paragraph separated by hyphens, covering aspects such as material feel, comfort, fit, durability, ease of use, and occasion suitability. Use simple, premium, and persuasive language that feels natural and human-like, avoid over-claiming or adding unverifiable details, and if any attribute is unclear from the image, use neutral terms such as soft material instead of guessing. The final output should be clean, structured, and ready for an e-commerce website with strong conversion potential.",
        "title_prompt": "You are an expert e-commerce copywriter specializing in kids' accessories. Analyze the provided product image carefully and perform a deep visual analysis of the item, identifying its type such as hairband, hair clips, cap, socks, bag, or similar accessory, along with its color, design elements, patterns, and overall style. Based on this analysis, generate a concise and SEO-friendly product title suitable for an e-commerce website that clearly reflects the key attributes like color, style, and product type. The title must be under 6 words, natural-sounding, and appealing for online shoppers. Do not include any extra words, explanations, symbols, or formatting. Return only the product title as plain text."
    },
    "footwear": {
        "image_prompt": "Stylish kids footwear product photo with clean background",
        "description_prompt": "You are an expert e-commerce copywriter specializing in kids' footwear. Analyze the provided product image carefully and perform a deep visual analysis of the item, identifying the type such as shoes, sandals, sneakers, boots, or slippers, along with material (estimate if not obvious), colors, patterns, sole type, closure type (velcro, slip-on, lace, buckle), design elements, and overall style. Based on this, generate a high-quality and accurate product listing. First, create a Product Title in plain text only without any symbols, formatting, or markdown, ensuring it is concise, SEO-friendly, and clearly reflects key attributes like color, style, and footwear type. Then write a Product Description in 2 or 3 short paragraphs highlighting comfort, durability, grip, ease of wear, and suitability for activities such as daily wear, outings, or playtime, focusing on benefits for both kids and parents. After that, include Key Features written in a single paragraph separated by hyphens, covering aspects such as cushioning, sole grip, lightweight feel, breathability, secure fit, and durability. Use simple, premium, and persuasive language that feels natural and human-like, avoid over-claiming or adding unverifiable details, and if any attribute is unclear from the image, use neutral terms such as soft material or comfortable sole instead of guessing. The final output should be clean, structured, and ready for an e-commerce website with strong conversion potential.",
        "title_prompt": "You are an expert e-commerce copywriter specializing in kids' footwear. Analyze the provided product image carefully and perform a deep visual analysis of the item, identifying the type such as shoes, sandals, sneakers, boots, or slippers, along with its color, design elements, patterns, and overall style. Based on this analysis, generate a concise and SEO-friendly product title suitable for an e-commerce website that clearly reflects key attributes like color, style, and footwear type. The title must be under 6 words, natural-sounding, and appealing for online shoppers. Do not include any extra words, explanations, symbols, or formatting. Return only the product title as plain text."
    }
}


rekognition = boto3.client("rekognition", region_name="us-east-1")
s3 = boto3.client("s3")

def classify_image(bucket, key):
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=5
    )
    labels = [label["Name"].lower() for label in response["Labels"]]
    print("Labels detected from Rekog service:",labels)
    clothing_keywords = ["clothing", "apparel", "shorts", "t-shirt", "dress", "sleeve", "pants", "jeans"]
    if "shoe" in labels or "sandal" in labels or "slipper" in labels:
        return "footwear"
    #elif "clothing" in labels or "apparel" in labels or "shorts" in labels or "t-shirt" in labels or "dress" in labels:
    elif any(keyword in labels for keyword in clothing_keywords):
        return "clothing"
    else:
        return "accessories"


def save_to_s3(bucket, key, bucket_key, original_key, d_key, data):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    print("bucket key:", bucket_key)
    print("original key:", original_key)
    print("d_key:",d_key)
    print("bucket:", bucket)
    print("Copy & Deleting original input file..")
    s3.copy(original_key, bucket, bucket_key)
    print("File successfully copied!")
    s3.delete_object(Bucket=bucket, Key=d_key)
    print("Successfully deleted!")



def generate_text_amazon(prompt,bucket,key):
    # Replace with OpenAI / Bedrock later
    print("Inside generate text.")
    client_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response["Body"].read()

    # Convert to base64
    # image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    

    # Call Bedrock model (Claude 3 Sonnet example)
    print("Calling bedrock..")
    try:
        response = client_bedrock.converse(
                modelId="us.amazon.nova-pro-v1:0",
                messages=[
                        {
                        "role": "user",
                        "content": [
                                {
                                "image": {
                                        "format": "jpeg",
                                        "source": {
                                        "bytes": image_bytes
                                        }
                                }
                                },
                                {
                                "text": prompt
                                }
                        ]
                        }
                ],
                inferenceConfig={
                        "maxTokens": 200
                }
                )
    except Exception as e:
        print("Exception Occurred: ",e)

    # Parse response
    print("RESULT:", response)
    # result = json.loads(response["body"].read())

    # Extract description
    # description = result["output"]["message"]["content"][0]["text"]
    description = response["output"]["message"]["content"][0]["text"]
    print("Model Final O/P:\n", description)


    return(description)

def generate_text_google(prompt,bucket,key):
    print("Inside generate text.")
    
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response["Body"].read()

    # Convert to base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    

    # Call Bedrock model (Claude 3 Sonnet example)
    print("Calling Google API..")
    try:
        text = os.environ.get('GCP_KEY') 
        client = genai.Client(api_key=text)
        response = client.models.generate_content(model="gemini-3.5-flash",contents=[prompt, image_base64])
    except Exception as e:
        print("Exception Occurred: ",e)

    # Parse response
    print("RESULT:", response.text)

    # Extract description
    # description = result["output"]["message"]["content"][0]["text"]
    # description = response["output"]["message"]["content"][0]["text"]
    # print("Model Final O/P:\n", description)


    # return(description)
    return(response.text)

def lambda_handler(event, context):
    try:
        # Get S3 details
        print("Event Details:",event)
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        print("Record:",record)
        print("KEY:",key)
        print("Bucket:",bucket)

        print(f"Processing file: {key}")
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        print("Sending key to rekog service ",key)

        # Step 1: Classify image
        category = classify_image(bucket, key)
        print(f"Detected category: {category}")

        # Step 2: Get prompts
        print("Getting prompts..")
        prompt_data = PROMPTS.get(category)

        # Step 3: Generate text content
        print("Calling generate text func..")
        if model == "amazon":
            description_output = generate_text_amazon(prompt_data["description_prompt"],bucket,key)
            title_output = generate_text_amazon(prompt_data["title_prompt"],bucket,key)
        else:
            description_output = generate_text_google(prompt_data["description_prompt"],bucket,key)
            title_output = generate_text_google(prompt_data["title_prompt"],bucket,key)

        # Step 4: Save output metadata
        #output_key = f"processed/{category}/{key.split('/')[-1]}.json"
        output_key = f"processed/{category}/{title_output}/{title_output}.json"
        # d_key = f"input/{key}"
        base = filename = os.path.basename(key)
        bucket_key = f"processed/{category}/{title_output}/{base}"
        original_key = {
            'Bucket': bucket,
            'Key': f"{key}"
            }

        save_to_s3(bucket, output_key, bucket_key, original_key, key, {
            "category": category,
            "original_image": key,
            "generated_title": title_output,
            "generated_desc": description_output
        })
        

        return {
            "statusCode": 200,
            "body": json.dumps("Processing completed")
        }

    except Exception as e:
        print(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps("Error processing image")
        }