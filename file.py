import boto3
import json
import urllib.parse
import random
import base64
import time

PROMPTS = {
    "clothing": {
        "image_prompt": "A high-quality kids clothing product photo with soft pastel background, studio lighting",
        "description_prompt": "Generate a product description for the kids clothing item shown in the image, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
        "title_prompt": "Generate a product title for the kids clothing item shown in the image, do a deep anylsis on the design before giving the title for website listing, make sure the title is under 6 words and dont return anything else only prodouct title. Return product title as plain text (no markdown, no formatting)"
    },
    "accessories": {
        "image_prompt": "Minimal premium accessory product shot with white background",
        "description_prompt": "Generate a product description for the kids accessory item shown in the image, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
        "title_prompt": "Generate a product title for the kids accessories item shown in the image, do a deep anylsis on the design and give a title for website listing under 6 words. Return product title as plain text (no markdown, no formatting)"
    },
    "footwear": {
        "image_prompt": "Stylish kids footwear product photo with clean background",
        "description_prompt": "Generate a product description for the kids footwear item shown in the image, do a deep anlysis on the design and product then generate a accurate description, Return product title as plain text (no markdown, no formatting)",
        "title_prompt": "Generate a product title for the kids footwear item shown in the image, do a deep anylsis on the design and give a title for website listing under 6 words. Return product title as plain text (no markdown, no formatting)"
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
    if "shoe" in labels or "sandal" in labels or "slipper" in labels:
        return "footwear"
    elif "clothing" in labels or "apparel" in labels:
        return "clothing"
    else:
        return "accessories"


def save_to_s3(bucket, key, data):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )


def generate_text(prompt,bucket,key):
    # Replace with OpenAI / Bedrock later
    print("Inside generate text.")
    client_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response["Body"].read()

    # Convert to base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    body = {
    'inferenceConfig': { 
        "maxTokens": 500
    },
    "messages": [
        {
            "role": "user",
            "content": [
                # {
                #     "image": {
                #     "source": {
                #         "type": "base64",
                #         "media_type": "image/jpeg",
                #         "data": image_base64
                #     },
                # },
                # },
                {
                    "text": prompt
                }
            ]
        }
    ]
}

    # Call Bedrock model (Claude 3 Sonnet example)
    print("Calling bedrock..")
    try:
        response = client_bedrock.invoke_model(
            modelId="us.amazon.nova-2-lite-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
    except Exception as e:
        print("Exception Occurred: ",e)

    # Parse response
    print("RESULT:", response)
    result = json.loads(response["body"].read())

    # Extract description
    description = result["output"]["message"]["content"][0]["text"]
    print("Model Final O/P:\n", description)


    return(description)


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
        description_output = generate_text(prompt_data["description_prompt"],bucket,key)
        title_output = generate_text(prompt_data["title_prompt"],bucket,key)

        # Step 4: Save output metadata
        #output_key = f"processed/{category}/{key.split('/')[-1]}.json"
        output_key = f"processed/{category}/{title_output}.json"

        save_to_s3(bucket, output_key, {
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