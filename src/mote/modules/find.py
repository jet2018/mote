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

import json
import os
import re
import urllib.parse as ulpr

directory_path = os.path.dirname("/srv/web/meetbot/")
recognition_pattern = "(.*)[\-\.]([0-9]{4}-[0-9]{2}-[0-9]{2})-([0-9]{2}\.[0-9]{2})"


def find_meetings_by_substring(search_string: str):
    """
    Return list of meetings returned from search
    """
    try:
        meeting_dictionary = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if search_string in file and not file.endswith(".tgz"):
                    location = "%s/%s" % (root, str(file))
                    if "/srv/web/meetbot/teams/" not in location:
                        location_list = location.replace("/srv/web/meetbot/", "").split(
                            "/"
                        )
                        channel_name, meeting_date, meeting_filename = (
                            location_list[0],
                            location_list[1],
                            location_list[2],
                        )
                        if ".log.html" in meeting_filename:
                            meeting_log_filename = meeting_filename
                            meeting_summary_filename = meeting_filename.replace(
                                ".log.html", ".html"
                            )
                            meeting_title = re.search(
                                recognition_pattern,
                                meeting_filename.replace(".log.html", ""),
                            )
                            meeting_object = {
                                "topic": meeting_title.group(1),
                                "channel": channel_name,
                                "date": meeting_date,
                                "time": meeting_title.group(3),
                                "url": {
                                    "logs": "https://meetbot-raw.fedoraproject.org/%s/%s/%s"
                                    % (
                                        channel_name,
                                        meeting_date,
                                        meeting_log_filename,
                                    ),
                                    "summary": "https://meetbot-raw.fedoraproject.org/%s/%s/%s"
                                    % (
                                        channel_name,
                                        meeting_date,
                                        meeting_summary_filename,
                                    ),
                                },
                                "slug": {
                                    "logs": ulpr.quote(
                                        "/%s/%s/%s"
                                        % (
                                            channel_name,
                                            meeting_date,
                                            meeting_log_filename,
                                        ),
                                        safe=":/?",
                                    ),
                                    "summary": ulpr.quote(
                                        "/%s/%s/%s"
                                        % (
                                            channel_name,
                                            meeting_date,
                                            meeting_summary_filename,
                                        ),
                                        safe=":/?",
                                    ),
                                },
                            }
                            meeting_dictionary.append(meeting_object)
        return True, meeting_dictionary
    except Exception as expt:
        return False, {"exception": str(expt)}


if __name__ == "__main__":
    print(json.dumps(find_meetings_by_substring(input()), indent=4))
