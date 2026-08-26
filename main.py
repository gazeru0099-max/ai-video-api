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

# 🌐 サーバーの本体をここで正しく定義します（これでエラーが消えます！）
app = Flask(__name__)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_ai_captions_auto(images):
    image_count = len(images)
    import requests
    image_contents = []
    for img in images:
        base64_image = encode_image(img)
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    prompt_text = (
        f"添付した {image_count} 枚の写真を順番使って、SNS用のショート動画を作ります。\n"
        f"それぞれの写真にぴったり合う、おしゃれで短い日本語のテロップ（10文字以内）を【合計 {image_count} 個】考えてください。\n"
        f"出力は、余計な説明や数字（1. など）は一切含めず、改行で区切った {image_count} 行の文字だけを出力してください。"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt_text}, *image_contents]}],
        "max_tokens": 200
    }

    try:
        response = requests.post("https://openai.com", headers=headers, json=payload)
        response_json = response.json()
        if "error" in response_json:
            return [f"思い出の一枚 {i+1}" for i in range(image_count)]
        result_text = response_json['choices']['message']['content'].strip()
        titles = [line.strip() for line in result_text.split('\n') if line.strip()]
        while len(titles) < image_count:
            titles.append("楽しい時間")
        return titles[:image_count]
    except:
        return [f"思い出の一枚 {i+1}" for i in range(image_count)]

def generate_video_process():
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
    from PIL import ImageDraw, ImageFont

    raw_images = []
    for ext in ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG'):
        raw_images.extend(glob.glob(ext))
        
    unique_images = list(set([os.path.abspath(img) for img in raw_images if not os.path.basename(img).startswith('temp_')]))
    images = [os.path.basename(path) for path in unique_images]
    images.sort()

    if not images:
        return None

    titles = get_ai_captions_auto(images)
    clips = []
    W, H = 1080, 1920

    for i, img_path in enumerate(images):
        duration = 2
        fps = 24
        total_frames = duration * fps
        base_img = PIL.Image.open(img_path).resize((W, H))
        frame_paths = []
        
        for f in range(total_frames):
            zoom_factor = 1.0 + (0.08 * (f / total_frames))
            z_w, z_h = int(W * zoom_factor), int(H * zoom_factor)
            zoomed_img = base_img.resize((z_w, z_h))
            left = (z_w - W) // 2
            top = (z_h - H) // 2
            frame_img = zoomed_img.crop((left, top, left + W, top + H))
            
            overlay = PIL.Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            font_paths = ["C:\\Windows\\Fonts\\meiryo.ttc", "C:\\Windows\\Fonts\\msmincho.ttc", "arial.ttf"]
            font = None
            for path in font_paths:
                if os.path.exists(path):
                    try: font = ImageFont.truetype(path, 60); break
                    except: continue
            if font is None: font = ImageFont.load_default()
            
            text = titles[i]
            tw, th = 400, 70
            try:
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0, 0), text, font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                else:
                    tw, th = draw.textsize(text, font=font)
            except: pass
                
            x = (W - tw) / 2
            y = H - th - 250
            
            padding_x, padding_y = 40, 20
            rect_left = x - padding_x
            rect_top = y - padding_y
            rect_right = x + tw + padding_x
            rect_bottom = y + th + padding_y + 10
            
            draw.rectangle([rect_left, rect_top, rect_right, rect_bottom], fill=(0, 0, 0, 140))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            final_frame = PIL.Image.alpha_composite(frame_img.convert("RGBA"), overlay).convert("RGB")
            frame_file = f"temp_frame_{i}_{f}.jpg"
            frame_file = os.path.abspath(frame_file)
            final_frame.save(frame_file)
            frame_paths.append(frame_file)
            
        frame_clips = [ImageClip(p).set_duration(1/fps) for p in frame_paths]
        sub_video = concatenate_videoclips(frame_clips, method="chain")
        clips.append(sub_video)

    video = concatenate_videoclips(clips, method="compose")
    
    bgm_filename = "bgm.mp3"
    if os.path.exists(bgm_filename):
        audio_clip = AudioFileClip(bgm_filename).set_duration(video.duration)
        video = video.set_audio(audio_clip)

    output_filename = "output.mp4"
    video.write_videofile(output_filename, fps=fps, codec="libx264", audio_codec="aac")
    
    for i in range(len(images)):
        for f in range(total_frames):
            temp_file = f"temp_frame_{i}_{f}.jpg"
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    return output_filename

# 🚀 【本物作成・保存版】Bubbleからのリクエストをここでガッチリ受け取ります！
@app.route('/make_video', methods=['POST'])
def api_make_video():
    print("📥 Bubbleから本物の動画生成指示を受信しました！")
    try:
        output_file = generate_video_process()
        
        if output_file and os.path.exists(output_file):
            print(f"📤 動画「{output_file}」の保存が完了しました！")
            return jsonify({
                "status": "success",
                "message": "動画の作成とパソコンへの保存が完了しました！"
            }), 200
        else:
            return jsonify({"error": "動画の生成に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": f"エラーが発生しました: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# 📥 サーバーに保存された動画をパソコンに持ってくるためのダウンロード窓口
@app.route('/download_video', methods=['GET'])
def download_video():
    if os.path.exists("output.mp4"):
        return send_file("output.mp4", mimetype='video/mp4', as_attachment=True)
    return jsonify({"error": "動画ファイルが見つかりません"}), 404
