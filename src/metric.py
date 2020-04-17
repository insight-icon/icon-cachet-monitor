from tcp_latency import measure_latency


def get_latency(url: str, runs: int = 10):
    domain_name = url.replace("https://", "").replace("/api/v3", "")
    return measure_latency(host=domain_name, runs=runs)


def get_avg_latency(url: str, num_runs: int = 5):
    avg = sum(get_latency(url, num_runs)) / num_runs
    return avg


# print(get_avg_latency('https://test-ctz.solidwallet.io'))

# url = 'https://zicon.net.solidwallet.io'
url = 'ctz.solidwallet.io/api/v3'
print(get_latency(url))
print(get_avg_latency(url))
#
# print(get_latency('https://google.com'))
