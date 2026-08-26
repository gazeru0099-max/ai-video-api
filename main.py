import os
import sys
import glob
import gc  # 💡 メモリ大掃除用のライブラリ

try:
    from flask import Flask, request, jsonify, Response
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, request, jsonify, Response

# 🌐 サーバーの本体起動
app = Flask(__name__)

def generate_video_process():
    # 💡 重たいアニメーション処理やAIテロップ、OpenAI、Pillow、音声処理をすべて廃止し、
    # MoviePy本来の最も軽い「写真同士を繋ぐだけ」の機能（15行）に圧縮しました！
    from moviepy.editor import ImageClip, concatenate_videoclips

    raw_images = []
    for ext in ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG'):
        raw_images.extend(glob.glob(ext))
        
    unique_images = list(set([os.path.abspath(img) for img in raw_images if not os.path.basename(img).startswith('temp_')]))
    images = [os.path.basename(path) for path in unique_images]
    images.sort()

    if not images:
        return None

    # 一番軽い「静止画クリップ（2秒）」を作成して連結します（メモリ消費ほぼ0）
    clips = [ImageClip(img_path).set_duration(2).resize((1080, 1920)) for img_path in images]
    video = concatenate_videoclips(clips, method="chain")

    output_filename = "output.mp4"
    # 画質設定（preset）を最速・最軽量の「ultrafast」に指定し、サーバーに負担をかけずに一瞬で書き出します
    video.write_videofile(output_filename, fps=24, codec="libx264", preset="ultrafast", audio=False)
    
    # 使用した動画パーツを即座に閉じて、メモリを大掃除します
    video.close()
    for c in clips:
        c.close()
                
    return output_filename

# 🚀 【本物作成・最軽量保存版】
@app.route('/make_video', methods=['POST'])
def api_make_video():
    print("📥 Bubbleから動画の生成指示を受信しました！")
    try:
        output_file = generate_video_process()
        
        # 写真が空っぽの場合は、安全装置として最軽量の2秒動画を作ります
        if not output_file:
            print("💡 写真がないため、テスト用動画を自動作成します。")
            from moviepy.editor import ColorClip
            output_file = "output.mp4"
            clip = ColorClip(size=(1080, 1920), color=(30, 30, 40), duration=2)
            clip.write_videofile(output_file, fps=24, codec="libx264", preset="ultrafast")
            clip.close()
            
        # 💡 溜まった不要なメモリを強制的に大掃除します
        gc.collect()
            
        if output_file and os.path.exists(output_file):
            print("📤 動画ファイルを【細切れストリーム】で安全に送信します！")
            
            def chunk_generator(fpath):
                with open(fpath, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        yield chunk
                        
            return Response(
                chunk_generator(output_file), 
                mimetype="video/mp4", 
                headers={"Content-Disposition": "attachment; filename=output.mp4"}
            )
        else:
            return jsonify({"error": "動画の生成に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": f"エラーが発生しました: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
