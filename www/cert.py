#!/usr/bin/env python3

# Copyright (c) 2014-2017  Regents of the University of California
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import Blueprint, render_template, abort, request, redirect, url_for, Response, current_app, make_response
from jinja2 import TemplateNotFound
from functools import wraps
import hashlib
from bson.objectid import ObjectId
import base64

import pyndn as ndn
import pyndn.security.v2.certificate_v2
from datetime import datetime

cert = Blueprint('cert', __name__, template_folder='templates')

from . import auth

# Public interface
@cert.route('/cert/get/', methods = ['GET'])
def get_certificate():
    name = request.args.get('name')
    isView = request.args.get('view')

    ndn_name = ndn.Name(str(name))

    cert = current_app.mongo.db.certs.find_one({'name': str(name)})
    if cert == None:
        abort(404)

    if not isView:
        response = make_response(cert['cert'])
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = 'attachment; filename=%s.ndncert' % str(ndn_name[-3])
        return response
    else:
        d = ndn.security.v2.certificate_v2.CertificateV2()
        d.wireDecode(bytearray(base64.b64decode(cert['cert'])))
        v = d.getValidityPeriod()

        notBefore = datetime.utcfromtimestamp(v.getNotBefore() / 1000)
        notAfter = datetime.utcfromtimestamp(v.getNotAfter() / 1000)
        cert['from'] = notBefore
        cert['to'] = notAfter
        now = datetime.now()
        cert['isValid'] = (notBefore <= now and now <= notAfter)
        cert['info'] = d

        return render_template('cert-show.html',
                               cert=cert, title=cert['name'])


# Public interface
@cert.route('/cert/list/', methods = ['GET'])
def get_certificates():
    certificates = current_app.mongo.db.certs.find().sort([('name', 1)])
    return make_response(render_template('cert-list.txt', certificates=certificates), 200, {
            'Content-Type': 'text/plain'
            })

@cert.route('/cert/list/html', methods = ['GET'])
def list_certs_html():
    certs = current_app.mongo.db.certs.find({ '$query': {},
                                         '$orderby': { 'name' : 1, 'operator.site_prefix': 1 }})
    certsWithInfo = []
    for cert in certs:
        info = cert
        d = ndn.security.v2.certificate_v2.CertificateV2()
        d.wireDecode(bytearray(base64.b64decode(cert['cert'])))
        v = d.getValidityPeriod()

        notBefore = datetime.utcfromtimestamp(v.getNotBefore() / 1000)
        notAfter = datetime.utcfromtimestamp(v.getNotAfter() / 1000)
        now = datetime.now()
        if notBefore <= now and now <= notAfter:
            info['to'] = notAfter.strftime('%Y-%m-%d')
            certsWithInfo.append(info)

    return render_template('cert-list.html',
                           certs=certsWithInfo, title="List of issued and not expired certificates")

@cert.route('/cert/list/admin', methods = ['GET'])
@auth.requires_auth
def list_certs_admin():
    certs = current_app.mongo.db.certs.find({ '$query': {},
                                         '$orderby': { 'name' : 1, 'operator.site_prefix': 1 }})
    return render_template('admin/cert-list.html',
                           certs=certs, title="List of issued certificates")

@cert.route('/admin/delete-cert/<id>', methods = ['GET', 'POST'])
@auth.requires_auth
def delete_cert(id):
    current_app.mongo.db.certs.remove({'_id': ObjectId(id)})
    return redirect(url_for('cert.list_certs_admin'))
