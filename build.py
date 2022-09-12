from profile_readme import get_github_context, ProfileGenerator
import feedparser
import requests

def get_weather(city):
    # declare the client. format defaults to the metric system (celcius, km/h, etc.)
    url = 'https://wttr.in/{}?format=3'.format(city)
    res = requests.get(url)
    return res.text

def get_feed(feed_url):
    d = feedparser.parse(feed_url)
    return d.entries[0:4]


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
            "![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)",
            "![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)",
            "![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)",
            "![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)",
            "![Markdown](https://img.shields.io/badge/markdown-%23000000.svg?style=for-the-badge&logo=markdown&logoColor=white)",
            "![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)",
            "![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)",
            "![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)"
        ],
    }
    context.update(**get_github_context("stephrobert"))
    ProfileGenerator.render(
        template_path="README-TEMPLATE.j2",
        output_path="README.md",
        context=context,
    )
