import azure.functions as func
import logging
from langchain_community.document_loaders import youtube

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="get_transcription", methods=["GET", "POST"])
def get_transcription(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    url = req.params.get("url")
    if not url:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        url = (body or {}).get("url")

    if not url:
        return func.HttpResponse(
            "Missing 'url'. Provide ?url=... or JSON { 'url': '...' }.",
            status_code=400,
        )

    try:
        loader = youtube.YoutubeLoader.from_youtube_url(url)
        transcript = loader.load()
        if not transcript:
            return func.HttpResponse(
                f"No transcript found for: {url}", status_code=404
            )
        content = transcript[0].page_content
        return func.HttpResponse(f"Transcript: {url}: {content}")
    except Exception as e:
        logging.exception("Failed to fetch transcript")
        return func.HttpResponse(
            f"Failed to fetch transcript for {url}: {str(e)}", status_code=502
        )