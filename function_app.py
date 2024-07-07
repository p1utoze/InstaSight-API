import azure.functions as func
import os
import logging
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="ai-sentiment", auth_level=func.AuthLevel.ANONYMOUS)
def ai_sentiment(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
        # Initialize Text Analytics client
    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    print('ENDPOINT:', endpoint)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    print(type(text_analytics_client))
    # Parse JSON body
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Invalid input",
             status_code=400
        )
    
    payload = list()
    for item in req_body:
        comments = item.pop("comments")
        results = text_analytics_client.analyze_sentiment(comments["data"])
        
        processed_results = []
        for result in results:
            processed_results.append({
                'comment': result.sentences[0].text,
                'sentiment': result.sentiment,
                "scores": list(result.confidence_scores.items())
            }
            )
        payload.append({
            **item,
            "comments":processed_results
        })
        

    return func.HttpResponse(f"{payload}", mimetype="application/json", status_code=200)

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )