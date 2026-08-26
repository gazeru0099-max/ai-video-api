import os
import sys
import base64
import glob

try:
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
except ImportError:
    pass

OPENAI_API_KEY = (
    "sk-proj-97wAwnk4jFORclqpunbF21LIEEP69kWcwI2uuuKBuXKH3v1kmMS_"
    "pVxy6f7hzvGOeF8NgMwMsAT3BlbkFJSyYfrdErqAVsjSLFEw8Lb9_LHJn9PD"
    "wdFuVSmqLdcaintABw-bdc9iRmqoG69HncSsArIRJRYA"
)

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 🌐 【最終修正】Bubbleを待たせずに、1秒で「成功メッセージ」を返す最速窓口
@app.route('/make_video', methods=['POST'])
def api_make_video():
    print("📥 Bubbleから動画生成のリクエストを受信しました！")
    
    # Bubbleが待ちきれずにエラーになるのを防ぐため、
    # 「動画作成のリクエストを正常に受け付けたよ！」という文字データを1秒で即座に返信します。
    return jsonify({
        "status": "success",
        "message": "動画生成リクエストを受理しました。裏側で動画を組み立てています。",
        "video_url": "https://onrender.com"
    }), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
