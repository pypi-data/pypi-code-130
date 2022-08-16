import time
from elasticsearch import Elasticsearch
from flask import request, session, render_template, current_app, url_for, redirect, Blueprint
from urllib.parse import quote
import base64

bp = Blueprint('host', __name__)


def authorize_url_and_session():
    state = request.args['state']
    myredirect = base64.b64encode(request.full_path.encode())
    redirect_url = quote(
        current_app.config['EXTERNAL_URL'] + url_for('oauth.oauthredirect', myredirect=myredirect))
    session['state'] = state
    session['UserId'] = request.args['fromuser']
    wx_authrize = f"https://open.weixin.qq.com/connect/oauth2/authorize?"\
        f"appid={current_app.config['WEWORK_CORPID']}&redirect_uri={redirect_url}&response_type=code"\
        f"&scope=snsapi_base&state={state}#wechat_redirect"

    return wx_authrize


@bp.route('/hostlist/', methods=['GET'])
def hostlist():

    if not session.get('Authorized'):
        return redirect(authorize_url_and_session())

    from_ = int(request.args.get('from', 0))
    size = int(request.args.get('size', current_app.config['ES_SIZE']))

    from_ = 0 if from_ < 0 else from_
    size = 1 if size < 0 else size

    es = Elasticsearch(current_app.config['ES_HOSTS'])
    index = f"zabbix-host-info-{time.strftime('%Y.%m.%d', time.localtime())}"
    res = es.search(index=index, q=request.args.get(
        'q'), timeout=current_app.config['ES_TIMEOUT'], from_=from_, size=current_app.config['ES_SIZE'])
    # try:
    #     res = es.search(index=index, q=request.args.get('q'), timeout=current_app.config['ES_TIMEOUT'], from_=from_, size=current_app.config['ES_SIZE'])
    # except ElasticsearchException as e:
    #     current_app.logger.exception(e)
    #     raise werkzeug.exceptions.InternalServerError()

    return render_template('hostlist.html.j2', data=res, from_=from_, size=size)


@bp.route('/hostdetail/<id>', methods=['GET'])
def hostdetail(id):
    if not session.get('Authorized'):
        return redirect(authorize_url_and_session())

    es = Elasticsearch(current_app.config['ES_HOSTS'])
    index = f"zabbix-host-info-{time.strftime('%Y.%m.%d', time.localtime())}"
    res = es.get(index=index, id=id)

    return render_template('hostdetail.html.j2', data=res)
