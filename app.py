import random
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "cute_rock_paper_scissors_secret_key"

CHOICES = ["rock", "scissors", "paper"]
EMOJI = {"rock": "✊", "scissors": "✌️", "paper": "✋"}
CN = {"rock": "石头", "scissors": "剪刀", "paper": "布"}


def judge(player: str, computer: str) -> str:
    """返回 'win' / 'lose' / 'draw'"""
    if player == computer:
        return "draw"
    rules = {
        ("rock", "scissors"): "win",
        ("scissors", "paper"): "win",
        ("paper", "rock"): "win",
    }
    return rules.get((player, computer), "lose")


def init_game():
    session["player_score"] = 0
    session["computer_score"] = 0
    session["rounds"] = 0
    session["game_over"] = False
    session["winner"] = None


@app.route("/")
def index():
    if "player_score" not in session:
        init_game()
    return render_template("index.html")


@app.route("/play", methods=["POST"])
def play():
    if "player_score" not in session:
        init_game()

    if session.get("game_over"):
        return jsonify({"error": "游戏已结束，请重新开始"}), 400

    data = request.get_json()
    player_choice = data.get("choice")

    if player_choice not in CHOICES:
        return jsonify({"error": "无效选择"}), 400

    computer_choice = random.choice(CHOICES)
    result = judge(player_choice, computer_choice)

    session["rounds"] += 1

    if result == "win":
        session["player_score"] += 1
    elif result == "lose":
        session["computer_score"] += 1

    # 三局两胜判定
    if session["player_score"] == 2 or session["computer_score"] == 2:
        session["game_over"] = True
        session["winner"] = (
            "player" if session["player_score"] == 2 else "computer"
        )

    resp = {
        "player_choice": player_choice,
        "player_emoji": EMOJI[player_choice],
        "player_cn": CN[player_choice],
        "computer_choice": computer_choice,
        "computer_emoji": EMOJI[computer_choice],
        "computer_cn": CN[computer_choice],
        "result": result,
        "player_score": session["player_score"],
        "computer_score": session["computer_score"],
        "rounds": session["rounds"],
        "game_over": session["game_over"],
        "winner": session.get("winner"),
    }
    return jsonify(resp)


@app.route("/reset", methods=["POST"])
def reset():
    init_game()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
