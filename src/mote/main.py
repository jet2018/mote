"""
    Copyright (c) 2021 Fedora Websites and Apps

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import re

import click
from flask import Flask, abort, jsonify, render_template, request

from mote.__init__ import __version__
from mote.modules.call import (
    fetch_channel_dict,
    fetch_datetxt_dict,
    fetch_meeting_content,
    fetch_meeting_dict,
)
from mote.modules.find import find_meetings_by_substring
from mote.modules.late import fetch_recent_meetings

main = Flask(__name__)
recognition_pattern = "(.*)[\-\.]([0-9]{4}-[0-9]{2}-[0-9]{2})-([0-9]{2}\.[0-9]{2})"


@main.get("/fragedpt/")
def fragedpt():
    rqstdata = request.args.get("rqstdata")
    response = {}
    if rqstdata == "listchan":
        chanobjc = fetch_channel_dict()
        if chanobjc[0]:
            response = chanobjc[1]
        else:
            print("Channel list could not be retrieved")
    elif rqstdata == "listdate":
        channame = request.args.get("channame")
        dateobjc = fetch_datetxt_dict(channame)
        if dateobjc[0]:
            response = dateobjc[1]
        else:
            print("Date list could not be retrieved")
    elif rqstdata == "listmeet":
        channame = request.args.get("channame")
        datename = request.args.get("datename")
        meetobjc = fetch_meeting_dict(channame, datename)
        if meetobjc[0]:
            response = meetobjc[1]
        else:
            print("Meeting list could not be retrieved")
    elif rqstdata == "srchmeet":
        srchtext = request.args.get("srchtext")
        srchrslt = find_meetings_by_substring(srchtext)
        if srchrslt[0]:
            response = srchrslt[1]
        else:
            print("Meetings could not be looked up")
    elif rqstdata == "rcntlsdy":
        meetlist = fetch_recent_meetings(1)
        if meetlist[0]:
            response = meetlist[1]
        else:
            print("List of recent meetings could not retrieved (last day)")
    elif rqstdata == "rcntlswk":
        meetlist = fetch_recent_meetings(7)
        if meetlist[0]:
            response = meetlist[1]
        else:
            print("List of recent meetings could not retrieved (last week)")
    return jsonify(response)


@main.get("/<channame>/<cldrdate>/<path:meetname>")
def statfile(channame, cldrdate, meetname):
    meetname = meetname.replace(".log.html", "").replace(".html", "")
    meeting_title = re.search(recognition_pattern, meetname)
    meetpath = "/srv/web/meetbot" + request.path
    print(meetpath)
    if meetpath[-1] == "/":
        meetpath = meetpath[0:-1]
    meetcont = fetch_meeting_content(meetpath)
    if meetcont[0]:
        if ".log.html" in request.path:
            typecont = "Logs"
        elif ".html" in request.path:
            typecont = "Minutes"
        else:
            typecont = "Contents"
        return render_template(
            "statfile.html",
            channame=channame,
            cldrdate=cldrdate,
            meetname=meeting_title.group(1),
            timetext=meeting_title.group(3),
            typecont=typecont,
            meetcont=meetcont[1],
        )
    else:
        abort(404)


@main.get("/")
def mainpage():
    return render_template("mainpage.html")


@click.command()
@click.option(
    "-p", "--portdata", "portdata", help="Set the port value [0-65536]", default="9696"
)
@click.option(
    "-6",
    "--ipprotv6",
    "netprotc",
    flag_value="ipprotv6",
    help="Start the server on an IPv6 address",
)
@click.option(
    "-4",
    "--ipprotv4",
    "netprotc",
    flag_value="ipprotv4",
    help="Start the server on an IPv4 address",
)
@click.version_option(version=__version__, prog_name="Fragment")
def mainfunc(portdata, netprotc):
    print(" * Starting Fragment...")
    print(" * Port number : " + str(portdata))
    netpdata = ""
    if netprotc == "ipprotv6":
        print(" * IP version  : 6")
        netpdata = "::"
    elif netprotc == "ipprotv4":
        print(" * IP version  : 4")
        netpdata = "0.0.0.0"
    main.config["TEMPLATES_AUTO_RELOAD"] = True
    main.run(port=portdata, host=netpdata)


if __name__ == "__main__":
    mainfunc()
