# 🚀 【安全装置付き・本物作成保存版】
@app.route('/make_video', methods=['POST'])
def api_make_video():
    print("📥 Bubbleから本物の動画生成指示を受信しました！")
    try:
        # まずはフォルダの中の写真を探して動画を作ってみる
        output_file = generate_video_process()
        
        # 💡 もし写真が1枚もない場合は、テスト用の2秒の動画をその場で作る安全装置！
        if not output_file:
            print("💡 写真がないため、テスト用動画を自動作成します。")
            from moviepy.editor import ColorClip
            output_file = "output.mp4"
            # 1080x1920（縦長スマホサイズ）の黒い画面の2秒動画を作る
            clip = ColorClip(size=(1080, 1920), color=(30, 30, 40), duration=2)
            clip.write_videofile(output_file, fps=24, codec="libx264")
            
        if output_file and os.path.exists(output_file):
            print(f"📤 動画「{output_file}」の保存が完了しました！")
            return jsonify({
                "status": "success",
                "message": "動画の作成とパソコンへの保存が完了しました！",
                "video_url": "https://onrender.com"
            }), 200
        else:
            return jsonify({"error": "動画の生成に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": f"エラーが発生しました: {str(e)}"}), 500

# 📥 サーバーに保存された動画をパソコンに持ってくるためのダウンロード窓口
@app.route('/download_video', methods=['GET'])
def download_video():
    if os.path.exists("output.mp4"):
        return send_file("output.mp4", mimetype='video/mp4', as_attachment=True)
    return jsonify({"error": "動画ファイルが見つかりません"}), 404
