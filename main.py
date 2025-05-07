from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_constitutional_judgement(shizi_number: int) -> dict:
    base_id = 310181
    initial_doc_id = base_id + shizi_number
    max_attempts = 20

    for offset in range(max_attempts):
        current_doc_id = initial_doc_id + offset
        url = f"https://cons.judicial.gov.tw/docdata.aspx?fid=100&id={current_doc_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        title_li = soup.find("li", class_="text", title="解釋字號")
        if not title_li or f"釋字第{shizi_number}號" not in title_li.text:
            continue

        expl_tags = soup.find_all("pre", title="解釋文")
        reason_tags = soup.find_all("pre", title="理由書")
        explanation = "\n".join(tag.get_text(separator='\n').strip() for tag in expl_tags)
        reason = "\n".join(tag.get_text(separator='\n').strip() for tag in reason_tags)

        return {
            "解釋字號": title_li.text.strip(),
            "解釋文": explanation or "(無解釋文)",
            "理由書": reason or "(無理由書)",
            "來源網址": url
        }

    return {"error": f"查無釋字第{shizi_number}號之公開解釋內容。"}

@app.route("/judgement/<int:shizi_number>", methods=["GET"])
def get_judgement(shizi_number):
    result = fetch_constitutional_judgement(shizi_number)
    status_code = 200 if "error" not in result else 404
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
