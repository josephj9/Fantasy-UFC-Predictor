from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import joblib  
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
model = tf.keras.models.load_model("fight_predictor.h5")
scaler = joblib.load("scaler.pkl")


import os
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Fighter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    reach_cm = db.Column(db.Float)
    stance = db.Column(db.String(50))
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    red_current_lose_streak = db.Column(db.Integer)
    red_current_win_streak = db.Column(db.Integer)
    red_longest_win_streak = db.Column(db.Integer)
    blue_current_lose_streak = db.Column(db.Integer)
    blue_current_win_streak = db.Column(db.Integer)
    blue_longest_win_streak = db.Column(db.Integer)
    red_total_rounds_fought = db.Column(db.Integer)
    blue_total_rounds_fought = db.Column(db.Integer)
    red_total_title_bouts = db.Column(db.Integer)
    blue_total_title_bouts = db.Column(db.Integer)
    red_wins_by_ko = db.Column(db.Integer)
    red_wins_by_submission = db.Column(db.Integer)
    red_wins_by_decision_unanimous = db.Column(db.Integer)
    blue_wins_by_ko = db.Column(db.Integer)
    blue_wins_by_submission = db.Column(db.Integer)
    blue_wins_by_decision_unanimous = db.Column(db.Integer)
    red_avg_sig_str_landed = db.Column(db.Float)
    red_avg_sig_str_pct = db.Column(db.Float)
    red_avg_sub_att = db.Column(db.Float)
    red_avg_td_landed = db.Column(db.Float)
    red_avg_td_pct = db.Column(db.Float)
    blue_avg_sig_str_landed = db.Column(db.Float)
    blue_avg_sig_str_pct = db.Column(db.Float)
    blue_avg_sub_att = db.Column(db.Float)
    blue_avg_td_landed = db.Column(db.Float)
    blue_avg_td_pct = db.Column(db.Float)
    red_odds = db.Column(db.Float)
    blue_odds = db.Column(db.Float)
    red_expected_value = db.Column(db.Float)
    blue_expected_value = db.Column(db.Float)
    red_dec_odds = db.Column(db.Float)
    blue_dec_odds = db.Column(db.Float)
    rsub_odds = db.Column(db.Float)
    bsub_odds = db.Column(db.Float)
    rko_odds = db.Column(db.Float)
    bko_odds = db.Column(db.Float)


    def to_dict(self):
        return {column.name: (0 if getattr(self, column.name) is None or pd.isna(getattr(self, column.name)) else getattr(self, column.name)) for column in self.__table__.columns}


    def __repr__(self):
        return f'Fighter {self.name}'

def populate_db():
    if Fighter.query.first():
        print("Database already populated. Skipping insertion.")
        return
    data = pd.read_csv("ufc-master.csv")

    data.fillna({"RedFighter": "", "RedStance": "", "RedAge": 0, "RedHeightCms": 0, "RedWeightLbs": 0,
                 "RedReachCms": 0, "RedWins": 0, "RedLosses": 0, "RedDraws": 0}, inplace=True)

    fighters = []

    for _, row in data.iterrows():
        fighter = Fighter.query.filter_by(name=row['RedFighter']).first()

        if fighter:
            if int(row['RedAge']) > fighter.age: 
                fighter.age = int(row['RedAge'])
        else:
            fighter = Fighter(
                name=row['RedFighter'],
                age=int(row['RedAge']),
                height_cm=float(row['RedHeightCms']),
                weight_kg=float(row['RedWeightLbs']) , 
                reach_cm=float(row['RedReachCms']),
                stance=row['RedStance'],
                wins=int(row['RedWins']),
                losses=int(row['RedLosses']),
                draws=int(row['RedDraws']),
                red_current_lose_streak=int(row['RedCurrentLoseStreak']),
                red_current_win_streak=int(row['RedCurrentWinStreak']),
                red_longest_win_streak=int(row['RedLongestWinStreak']),
                blue_current_lose_streak=int(row['BlueCurrentLoseStreak']),
                blue_current_win_streak=int(row['BlueCurrentWinStreak']),
                blue_longest_win_streak=int(row['BlueLongestWinStreak']),
                red_total_rounds_fought=int(row['RedTotalRoundsFought']),
                blue_total_rounds_fought=int(row['BlueTotalRoundsFought']),
                red_total_title_bouts=int(row['RedTotalTitleBouts']),
                blue_total_title_bouts=int(row['BlueTotalTitleBouts']),
                red_wins_by_ko=int(row['RedWinsByKO']),
                red_wins_by_submission=int(row['RedWinsBySubmission']),
                red_wins_by_decision_unanimous=int(row['RedWinsByDecisionUnanimous']),
                blue_wins_by_ko=int(row['BlueWinsByKO']),
                blue_wins_by_submission=int(row['BlueWinsBySubmission']),
                blue_wins_by_decision_unanimous=int(row['BlueWinsByDecisionUnanimous']),
                red_avg_sig_str_landed=float(row['RedAvgSigStrLanded']),
                red_avg_sig_str_pct=float(row['RedAvgSigStrPct']),
                red_avg_sub_att=float(row['RedAvgSubAtt']),
                red_avg_td_landed=float(row['RedAvgTDLanded']),
                red_avg_td_pct=float(row['RedAvgTDPct']),
                blue_avg_sig_str_landed=float(row['BlueAvgSigStrLanded']),
                blue_avg_sig_str_pct=float(row['BlueAvgSigStrPct']),
                blue_avg_sub_att=float(row['BlueAvgSubAtt']),
                blue_avg_td_landed=float(row['BlueAvgTDLanded']),
                blue_avg_td_pct=float(row['BlueAvgTDPct']),
                red_odds=float(row['RedOdds']),
                blue_odds=float(row['BlueOdds']),
                red_expected_value=float(row['RedExpectedValue']),
                blue_expected_value=float(row['BlueExpectedValue']),
                red_dec_odds=float(row['RedDecOdds']),
                blue_dec_odds=float(row['BlueDecOdds']),
                rsub_odds=float(row['RSubOdds']),
                bsub_odds=float(row['BSubOdds']),
                rko_odds=float(row['RKOOdds']),
                bko_odds=float(row['BKOOdds'])
            )

        fighters.append(db.session.merge(fighter))

    db.session.add_all(fighters)
    db.session.commit()
    print(f"Inserted {len(fighters)} fighters into the database.")


    
@app.route("/fighters", methods=["GET"])
def get_fighters():
    fighters = Fighter.query.all()
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Loaded Fighters: {[f.to_dict() for f in fighters]}")
    return jsonify([f.to_dict() for f in fighters])


@app.route("/fighter/<name>", methods=["GET"])
def get_fighter(name):
    #query the database (get fighers from the database)
    fighter = Fighter.query.filter_by(name=name).first()
    #return as json
    if (fighter):
        return jsonify(fighter.to_dict())
    return jsonify({"error" : "Fighter not Found!"}), 404

def predict_fight(red_stats, blue_stats):
    #put stats into numpy array
    stats = np.array([
        red_stats["red_current_lose_streak"], red_stats["red_current_win_streak"], red_stats["red_longest_win_streak"],
        blue_stats["blue_current_lose_streak"], blue_stats["blue_current_win_streak"], blue_stats["blue_longest_win_streak"],
        red_stats["losses"], red_stats["wins"], blue_stats["losses"], blue_stats["wins"],
        red_stats["red_total_rounds_fought"], blue_stats["blue_total_rounds_fought"],
        red_stats["red_total_title_bouts"], blue_stats["blue_total_title_bouts"],
        red_stats["red_wins_by_ko"], red_stats["red_wins_by_submission"], red_stats["red_wins_by_decision_unanimous"],
        blue_stats["blue_wins_by_ko"], blue_stats["blue_wins_by_submission"], blue_stats["blue_wins_by_decision_unanimous"],
        red_stats["red_avg_sig_str_landed"], red_stats["red_avg_sig_str_pct"],
        red_stats["red_avg_sub_att"], red_stats["red_avg_td_landed"], red_stats["red_avg_td_pct"],
        blue_stats["blue_avg_sig_str_landed"], blue_stats["blue_avg_sig_str_pct"],
        blue_stats["blue_avg_sub_att"], blue_stats["blue_avg_td_landed"], blue_stats["blue_avg_td_pct"],
        red_stats["height_cm"], red_stats["reach_cm"], red_stats["weight_kg"], red_stats["age"],
        blue_stats["height_cm"], blue_stats["reach_cm"], blue_stats["weight_kg"], blue_stats["age"],
        red_stats["red_odds"], blue_stats["blue_odds"], red_stats["red_expected_value"], blue_stats["blue_expected_value"],
        red_stats["red_dec_odds"], blue_stats["blue_dec_odds"], red_stats["rsub_odds"], blue_stats["bsub_odds"],
        red_stats["rko_odds"], blue_stats["bko_odds"]
    ]).reshape(1, -1)

    #transform scaled stats
    scaledStats = scaler.transform(stats)
    #prediction
    prediction = model.predict(scaledStats)[0][0]
    #check if predicton > 0.05
    return "Red Fighter Wins!" if prediction >= 0.5 else "Blue Fighter Wins!"

@app.route("/predict", methods=["POST"])
def predict():
    #get the data from request
    data = request.get_json()
    #get both fighters stats
    redFighter = Fighter.query.filter_by(name=data["red"]).first()
    blueFighter = Fighter.query.filter_by(name=data["blue"]).first()
    #error check
    if (not blueFighter or not redFighter):
        return jsonify({"error" : "Fighter Not Found!"}), 404
    #send to predict_fight
    winner = predict_fight(redFighter.to_dict(), blueFighter.to_dict())
    #reutrn jsonify
    return jsonify({"winner": winner})  


if __name__ == '__main__':
    # with app.app_context(): #run once 
        # db.create_all()
        # populate_db()
    app.run(debug=True) 

