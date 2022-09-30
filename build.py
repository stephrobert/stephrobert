#!/usr/bin/env python3
from profile_readme import get_github_context, ProfileGenerator
import feedparser
import requests

def get_weather(city):
    # declare the client. format defaults to the metric system (celcius, km/h, etc.)
    url = 'https://wttr.in/{}?m&format=3'.format(city)
    res = requests.get(url)
    return res.text

def get_feed(feed_url):
    feed = feedparser.parse(feed_url)
    entries = feed.entries
    from operator import itemgetter
    feed_sorted = sorted(entries, key=itemgetter('published_parsed'), reverse=True)

    return feed_sorted[0:4]


if __name__ == "__main__":
    weather = get_weather("Lille")
    last_posts = get_feed("https://blog.stephane-robert.info/feed.xml")
    context = {
        "weather" : weather,
        "last_posts": last_posts,
        "linkedin": {
            "url": "https://www.linkedin.com/in/stephanerobert1/",
            "badge": "![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)",
        },
        "twitter": {
            "url": "https://twitter.com/RobertStphane19/",
            "badge": "![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white)",
        },
        "badges": [
            "![Vagrant](https://img.shields.io/badge/vagrant-%231563FF.svg?style=for-the-badge&logo=vagrant&logoColor=white)",
            "![Packer](https://img.shields.io/badge/packer-%23E7EEF0.svg?style=for-the-badge&logo=packer&logoColor=%2302A8EF)",
            "![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)",
            "![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)",
            "![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)",
            "![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)",
            "![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)",
            "![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)",
            "![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)",
            "![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)",
            "![Markdown](https://img.shields.io/badge/markdown-%23000000.svg?style=for-the-badge&logo=markdown&logoColor=white)",
            "![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)",
            "![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)",
            "![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)",
            "![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)",
            "![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)",
            "![Apache](https://img.shields.io/badge/apache-%23D42029.svg?style=for-the-badge&logo=apache&logoColor=white)",
            "![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)",
            "![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)",
            "![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)",
            "![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)",            "![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)",
            "![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)",
            "![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)",
            "![GitLab CI](https://img.shields.io/badge/gitlab%20ci-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)",
            "![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)",
            "![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-%230D597F.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)",
            "![Cent OS](https://img.shields.io/badge/cent%20os-002260?style=for-the-badge&logo=centos&logoColor=F0F0F0)",
            "![Debian](https://img.shields.io/badge/Debian-D70A53?style=for-the-badge&logo=debian&logoColor=white)",
            "![Rocky Linux](https://img.shields.io/badge/-Rocky%20Linux-%2310B981?style=for-the-badge&logo=rockylinux&logoColor=white)",
            "![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)",
        ],
        "mykofi": {
            "url": "https://ko-fi.com/stephanerobert89902",
            "badge": "![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)"
        },
        "links": [
            {
                "title": "Vagrant",
                "link": "https://blog.stephane-robert.info/tags/vagrant/"
            },
            {
                "title": "Ansible",
                "link": "https://blog.stephane-robert.info/post/introduction-ansible/"
            },
            {
                "title": "Docker",
                "link": "https://blog.stephane-robert.info/tags/docker/"
            },
            {
                "title": "Kubernetes",
                "link": "https://blog.stephane-robert.info/tags/kubernetes/"
            },
            {
                "title": "Terraform",
                "link": "https://blog.stephane-robert.info/tags/terraform/"
            },
            {
                "title": "Gitlab-ci",
                "link": "https://blog.stephane-robert.info/tags/gitlab/"
            }
        ]
    }
    context.update(**get_github_context("stephrobert"))
    ProfileGenerator.render(
        template_path="README-TEMPLATE.j2",
        output_path="README.md",
        context=context,
    )
