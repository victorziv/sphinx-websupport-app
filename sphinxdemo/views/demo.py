from flask import Module, render_template, request, g, session, flash, \
     redirect, url_for, abort, jsonify
from sphinx.websupport import WebSupport

from sphinxdemo import conf

support = WebSupport(datadir=conf.OUTPUT_DIR)

demo = Module(__name__)

@demo.route('/docs/')
def docs():
    return redirect('/docs/contents')

@demo.route('/docs/<path:docname>')
def doc(docname):
    document = support.get_document(docname)
    return render_template('doc.html', document=document)

@demo.route('/docs/search')
def search():
    document = support.get_search_results(request.args.get('q', ''))
    return render_template('doc.html', document=document)

@demo.route('/docs/get_comments')
def get_comments():
    user_id = g.user.id if g.user else None
    node_id = request.args.get('node', '')
    data = support.get_comments(node_id, user_id)
    return jsonify(**data)

@demo.route('/docs/add_comment', methods=['POST'])
def add_comment():
    parent_id = request.form.get('parent', '')
    node_id = request.form.get('node', '')
    text = request.form.get('text', '')
    proposal = request.form.get('proposal', '')
    username = g.user.name if g.user is not None else 'Anonymous'
    comment = support.add_comment(text, node=node_id, parent=parent_id,
                                  username=username, proposal=proposal)
    return jsonify(comment=comment)

@demo.route('/docs/process_vote', methods=['POST'])
def process_vote():
    if g.user is None:
        abort(401)
    comment_id = request.form.get('comment_id')
    value = request.form.get('value')
    if value is None or comment_id is None:
        abort(400)
    support.process_vote(comment_id, g.user.id, value)
    return "success"
