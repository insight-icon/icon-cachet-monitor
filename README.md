# ICON Cachet URL Monitoring

Service that: 
1. Updates the status of components by monitoring a set of endpoints, both REST and jsonrpc. 
1. Pushes latency metrics of components

## Usage

1. Clone the project
2. Rename `config.json.example` to 'config.json'
3. Edit `config.json` to suit your needs REMEMBER TO CHANGE THE API URL AND TOKEN
4. Run the script using `python cachetMonitor.py`
5. (Optional) setup cron script to execute the script automatic

###### Credits

- cachet-monitor: https://github.com/Gaz492/cachet-monitor
- Cachet Library: https://github.com/imlonghao/cachet.python