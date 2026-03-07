import os
import sqlite3
import helpers

from flask import Flask, render_template, request, redirect, flash
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))


conn = helpers.get_db()
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS hocalar (
               id SERIAL PRIMARY KEY, name TEXT, rating FLOAT, submissions INTEGER)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS comments (
               profId INTEGER REFERENCES hocalar(id), comment TEXT)""")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    name = request.args.get("hoca_adi", "").strip().lower()
    conn = helpers.get_db()
    cursor = conn.cursor()
    results = cursor.execute("SELECT * FROM hocalar WHERE name LIKE ?", (f"%{name}%",)).fetchall()
    conn.close()
    return render_template("search.html", results=results)


@app.route('/result')
def result():
    profId = request.args.get("id")
    conn = helpers.get_db()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM hocalar WHERE id = ?", (profId,)).fetchone()
    if not result:
        flash("Hoca bulunamadı. Lütfen geçerli bir ID girin.", "danger")
        conn.close()
        return redirect("/search")
    comments = cursor.execute("SELECT * FROM comments WHERE profId = ?", (profId,)).fetchall()
    conn.close()
    return render_template("result.html", result=result, comments=comments)
    


@app.route('/rate', methods=["POST"])
def rate():
    profId = int(request.form.get("profId"))
    rating = request.form.get("rating")
    if rating:
        rating = float(rating)
        if rating >= 1 and rating <=5:
            conn = helpers.get_db()
            cursor = conn.cursor()
            submissions = cursor.execute("SELECT submissions FROM hocalar WHERE id =?", (profId,)).fetchone()["submissions"]
            avgRating = cursor.execute("SELECT rating FROM hocalar WHERE id =?", (profId,)).fetchone()["rating"]
            if avgRating is None:
                avgRating = 0
            newRating = (avgRating * submissions + rating) / (submissions + 1)
            cursor.execute("UPDATE hocalar SET rating = ?, submissions = ? WHERE id =?", (newRating, submissions+1, profId,))
            conn.commit()
            conn.close()
            message = "Puanınız başarıyla kaydedildi. Teşekkür ederiz!"
            flash(message, "success")
            return redirect(f"/result?id={profId}")
        else:
            message = "Invalid rating value. Please enter a number between 1 and 5."
            flash(message, "danger")
            return redirect(f"/result?id={profId}")
    else:
            message = "Geçersiz puan değeri. Lütfen 1 ile 5 arasında bir sayı girin."
            flash(message, "danger")
            return redirect(f"/result?id={profId}")
        
    


@app.route('/comment', methods=["POST"])
def comment():
    profId = int(request.form.get("profId"))
    comment = request.form.get("comment")
    if comment:    
        conn = helpers.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (profId, comment) VALUES (?, ?)", (profId, comment))
        conn.commit()
        conn.close()
        message = "Yorumunuz başarıyla kaydedildi. Teşekkür ederiz!"
        flash(message, "success")
        return redirect(f"/result?id={profId}")
    else:
        message = "Yorum boş olamaz. Lütfen geçerli bir yorum girin."
        flash(message, "danger")
        return redirect(f"/result?id={profId}")
        



@app.route('/add', methods=["POST"])
def add():
    name = request.form.get('name', '').strip().lower()
    if name:
        conn = helpers.get_db()
        cursor = conn.cursor()
        data = cursor.execute("SELECT * FROM hocalar WHERE name = ?", (name,)).fetchone()
        if not data:
            cursor.execute("INSERT INTO hocalar (name) VALUES (?)", (name,))
            id = cursor.lastrowid
            message = f"Hoca '{name}' başarıyla eklendi!"
        else:
            id = data["id"]
            message = f"Hoca '{name}' zaten mevcut!"
        flash(message, "success")
        conn.commit()
        conn.close()
        return redirect(f'/result?id={id}')
    else:
        flash("Hoca adı boş olamaz. Lütfen geçerli bir isim girin.", "danger")
        return redirect("/")