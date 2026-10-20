"""Fetch the README's tool marks from the MIT-licensed Devicon project."""
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/devicons/devicon/master/'
TOOLS = {
    'typescript': 'typescript/typescript-original.svg',
    'python': 'python/python-original.svg',
    'react': 'react/react-original.svg',
    'nextjs': 'nextjs/nextjs-original.svg',
    'nodejs': 'nodejs/nodejs-original.svg',
    'java': 'java/java-original.svg',
    'spring': 'spring/spring-original.svg',
    'vue': 'vuejs/vuejs-original.svg',
    'angular': 'angular/angular-original.svg',
    'postgresql': 'postgresql/postgresql-original.svg',
    'mongodb': 'mongodb/mongodb-original.svg',
    'redis': 'redis/redis-original.svg',
    'kafka': 'apachekafka/apachekafka-original.svg',
    'rabbitmq': 'rabbitmq/rabbitmq-original.svg',
    'docker': 'docker/docker-original.svg',
    'kubernetes': 'kubernetes/kubernetes-original.svg',
    'aws': 'amazonwebservices/amazonwebservices-original-wordmark.svg',
    'gcp': 'googlecloud/googlecloud-original.svg',
    'azure': 'azure/azure-original.svg',
    'terraform': 'terraform/terraform-original.svg',
    'helm': 'helm/helm-original.svg',
    'jenkins': 'jenkins/jenkins-original.svg',
    'prometheus': 'prometheus/prometheus-original.svg',
    'grafana': 'grafana/grafana-original.svg',
    'opentelemetry': 'opentelemetry/opentelemetry-original.svg',
    'tensorflow': 'tensorflow/tensorflow-original.svg',
    'scikitlearn': 'scikitlearn/scikitlearn-original.svg',
    'javascript': 'javascript/javascript-original.svg',
    'firebase': 'firebase/firebase-original.svg',
    'html5': 'html5/html5-original.svg',
    'css3': 'css3/css3-original.svg',
    'tailwindcss': 'tailwindcss/tailwindcss-original.svg',
    'oracle': 'oracle/oracle-original.svg',
    'dynamodb': 'dynamodb/dynamodb-original.svg',
    'elasticsearch': 'elasticsearch/elasticsearch-original.svg',
    'kinesis': 'amazonwebservices/amazonwebservices-original-wordmark.svg',
    'eventhubs': 'azure/azure-original.svg',
    'camel': 'apache/apache-original.svg',
    'atlas': 'apache/apache-original.svg',
    'openshift': 'redhat/redhat-original.svg',
    'eks': 'amazonwebservices/amazonwebservices-original-wordmark.svg',
    'ansible': 'ansible/ansible-original.svg',
    'jaeger': 'jaegertracing/jaegertracing-original.svg',
    'logstash': 'logstash/logstash-original.svg',
    'kibana': 'kibana/kibana-original.svg',
    'git': 'git/git-original.svg',
    'github': 'github/github-original.svg',
    'maven': 'maven/maven-original.svg',
    'selenium': 'selenium/selenium-original.svg',
    'jira': 'jira/jira-original.svg',
}
for name, path in TOOLS.items():
    if (ROOT / 'assets/tools' / f'{name}.svg').exists():
        continue
    data = urlopen(BASE + 'icons/' + path).read()
    assert b'<svg' in data
    # A neutral tile keeps dark brand marks readable in both GitHub themes.
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    mark = ET.fromstring(data)
    mark.set('x', '4'); mark.set('y', '4')
    mark.set('width', '24'); mark.set('height', '24')
    tile = ET.Element('{http://www.w3.org/2000/svg}svg', {'viewBox': '0 0 32 32'})
    ET.SubElement(tile, '{http://www.w3.org/2000/svg}rect', {'width': '32', 'height': '32', 'rx': '6', 'fill': '#f6f7f9'})
    tile.append(mark)
    (ROOT / 'assets/tools' / f'{name}.svg').write_bytes(ET.tostring(tile))
    print(name)
(ROOT / 'assets/tools/LICENSE.devicon').write_bytes(urlopen(BASE+'LICENSE').read())
