import functools
import calendar
import logging
import io
import csv
from permissions import has_permission, edit_permission
import discordoauth2
from flask import request, redirect, render_template, url_for, make_response, send_file, Response
import flask
import flask_login
from flask_login import current_user, login_required
from datetime import datetime
from database import User, Quote, Guild, Calendar
from functools import lru_cache
from config import config


app = flask.Flask(__name__)
app.secret_key = config["flask"]["secret"]


login_manager = flask_login.LoginManager()
login_manager.init_app(app)

client = discordoauth2.Client(
    config["discord"]["id"],
    secret=config["discord"]["secret"],
    bot_token=config["discord"]["token"],
    redirect=config["discord"]["redirect"]
)


@login_manager.user_loader
def user_loader(user_id):
    return User.objects(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))


@app.context_processor
def inject_now():
    return {'now': datetime.now()}


@app.template_global("get_username")
@lru_cache(maxsize=25)
def jinja_get_username(user_id) -> str:
    query = User.objects(discord=user_id)
    if query.count() == 0:
        return "Anon"

    return query.first().display_name


@app.template_global("get_guildname")
@lru_cache(maxsize=10)
def get_guildname(guild_id):
    query = Guild.objects(guild_id=guild_id)
    if query.count() == 0:
        return "Anon"

    return query.first().name


@app.template_global("has_permission")
def has_permission_jinja(perm:str):
    return has_permission(perm)


def permissions(perms: str):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if has_permission(perms) and has_permission("site.view"):
                return f(*args, **kwargs)
            return redirect("/")
        return decorated_function
    return decorator


@app.route("/callback/")
def oauth2_callback():
    code = request.args.get("code")
    access = client.exchange_code(code)
    identify = access.fetch_identify()

    if User.objects(discord=identify["id"]).count() == 0:
        user = User(identify["username"], identify["id"]).save()
    else:
        user = User.objects(discord=identify["id"]).first()

    user.data = identify
    user.save()

    flask_login.login_user(user, remember=True)

    return redirect(url_for("index"))


@app.get("/login/")
def login():
    return redirect(client.generate_uri(scope=["identify"]))


@app.route("/logout/")
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))

@app.route('/')
def index():
    return render_template("index.html", nav="home")


@app.route('/test/')
@login_required
@permissions("site.admin")
def test_index():
    return render_template("test.html", nav="home", subnav="ipsum")


@app.route('/quotes/')
@login_required
@permissions("quotes.view")
def quotes_home():
    quotes = Quote.objects(users__contains=current_user.discord, enabled=True).order_by("dt")

    response = make_response(render_template("quotes/index.html", nav="quotes", subnav="quotes", quotes=quotes), 200)
    response.headers.add("Access-Control-Allow-Origin", "https://zurok.net/quotes/")

    return response


@app.route('/quotes/csv/')
@login_required
@permissions("quotes.view")
def quotes_csv():
    quotes = Quote.objects(users__contains=current_user.discord, enabled=True).order_by("dt")

    def generate():
        data = io.StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(("0", "Quote", "Date/Time", "Users"))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each log item
        for x, quote in enumerate(quotes):
            w.writerow((
                x+1,
                " | ".join([f"{q} - {jinja_get_username(u)}" for q, u in zip(quote.quotes, quote.users)]),
                quote.dt.strftime("%d/%m/%Y %H:%M"),
                len(set(quote.users))
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="quotes.csv")
    return response


@app.route('/quotes/admin/')
@login_required
@permissions("quotes.admin")
def quotes_admin():
    quotes = Quote.objects(enabled=True).order_by("dt")

    response = make_response(render_template("quotes/index.html", nav="quotes", subnav="admin", quotes=quotes), 200)
    response.headers.add("Access-Control-Allow-Origin", "https://zurok.net/quotes/")

    return response


@app.route('/quotes/', methods=['POST'])
@app.route('/quotes/admin/', methods=['POST'])
@login_required
@permissions("quotes.hide")
def quotes_hide():
    quote_id = request.json["quote"]
    if len(quote_id) != 24:
        return "Quote Not Found", 404

    query = Quote.objects(id=quote_id)

    if query.count() == 0:
        return "Quote Not Found", 404

    q = query.first()

    if current_user.discord not in q.users and not has_permission("quotes.admin"):
        return "Action Forbidden", 403

    q.enabled = False
    q.save()

    return "Quote Hidden", 200

@app.route("/quotes/board/")
@login_required
@permissions("quotes.view")
def quotes_board():
    scores = {x: {} for x in current_user.tags if x in []} #  discord serv ids are stored in tags of user data
    guild_names = {} # key: value -> server id: display name

    for tag in scores:
        for other_user in User.objects(tags__contains=tag):
            count = Quote.objects(users__contains=other_user.discord, enabled=True).count()
            if count > 0:
                scores[tag][other_user.display_name] = count

        scores[tag] = dict(sorted(scores[tag].items(), key=lambda item: item[1], reverse=True))

    return render_template("quotes/board.html", nav="quotes", subnav="board",
                           scores=scores, guilds=guild_names)


@app.route("/admin/")
@login_required
@permissions("admin.view")
def admin_home():
    return render_template("admin/index.html", nav="admin", subnav="admin")


current_year = datetime.now().year


@app.route("/calendar/")
@app.route("/calendar/<int:year>")
@login_required
@permissions("calendar.view")
def calendar_home(year:int=current_year):
    _year = min(current_year + 1, max(year, 2020))
    if year != _year:
        return redirect(url_for("calendar_home", year=_year))

    cal = calendar.Calendar(firstweekday=0)
    _months = cal.yeardayscalendar(year, width=1)

    months = []
    m: list[list[list[int]]]
    for m in _months:
        month = m[0]
        if len(month) == 4:
            month.append([0, 0, 0, 0, 0, 0, 0])
        if len(month) == 5:
            month.append([0, 0, 0, 0, 0, 0, 0])
        months.append(month)

    data = Calendar.objects(user_id=current_user.discord, year=year).first()
    if data is None:
        data = Calendar(user_id=current_user.discord, year=year).save()

    return render_template("calendar/index.html", nav="calendar", subnav="calendar",
                           year=year, months=months, m_names=calendar.month_name, data=data)

@app.route("/calendar/update-day/", methods=["POST"])
def calendar_update_day():
    data = request.json
    year_data = Calendar.objects(user_id=current_user.discord, year=data["year"]).first()

    if data["month"] not in year_data.days:
        year_data.days[data["month"]] = {}
    year_data.days[data["month"]][data["day"]] = data["mode"]

    year_data.save()

    return "OK", 200

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
