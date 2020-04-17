from tcp_latency import measure_latency
from src.utils import Utils

import logging

from pprint import pprint


def get_latency(url: str, runs: int = 3):
    domain_name = url.replace("https://", "").replace("/api/v3", "")
    print(domain_name)
    latency = measure_latency(host=domain_name, runs=runs)
    return latency


def get_avg_latency(url: str, num_runs: int = 5):
    avg = sum(get_latency(url, num_runs)) / num_runs
    # print(f'collecting latency from {url} resulting in {avg} ms latency')
    return avg


def post_latency_metric(url: str, metric_id: int):
    l = get_avg_latency(url)
    u = Utils()
    logging.debug("posting to metric id %s value %s" % (metric_id, l))
    u.postMetricsPointsByID(c_id=metric_id, value=float(l))


def get_metrics():
    u = Utils()
    m = u.getMetrics().json()
    pprint(m)

url = 'https://bicon.tracker.solidwallet.io/'

l = get_latency(url)
print(l)