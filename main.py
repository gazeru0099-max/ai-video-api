# 🚀 【本物作成・保存版】
@app.route('/make_video', methods=['POST'])
def api_make_video():
    print("📥 Bubbleから本物の動画生成指示を受信しました！")
    try:
        # 実際にフォルダの中の写真を使って動画（output.mp4）を組み立て・保存します！
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
